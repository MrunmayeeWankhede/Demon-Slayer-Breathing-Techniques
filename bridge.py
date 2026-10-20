"""Webcam + offline voice -> TouchDesigner. Python 3.11/3.12; see START_HERE.md.
Keyboard fallback in preview: 1..9 style, space pause/resume, q quit.
"""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import math
from pathlib import Path
import queue
import secrets
import sys
import threading
import time

import cv2
import mediapipe as mp
import numpy as np
from pythonosc.udp_client import SimpleUDPClient

STYLES = ['flame', 'water', 'mist', 'stone', 'love', 'wind', 'serpent', 'insect', 'sound']
ALIASES = {s: i for i, s in enumerate(STYLES)}
ALIASES['fire'] = 0
COMMANDS = {**ALIASES, 'stop': -1, 'start': -2}
ROOT = Path(__file__).resolve().parent


class CameraFeed:
    """Share only the newest clean frame over loopback; no video is recorded."""
    def __init__(self, port):
        self.latest = None
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_GET(self):
                if self.path != '/frame':
                    self.send_error(404)
                    return
                latest = owner.latest
                if latest is None or time.monotonic() - latest[0] > 1:
                    self.send_error(503, 'Waiting for camera')
                    return
                stamp, pixels = latest
                self.send_response(200)
                self.send_header('Content-Type', 'application/octet-stream')
                self.send_header('Content-Length', str(len(pixels)))
                self.send_header('Cache-Control', 'no-store')
                self.send_header('X-Breathing-Frame', str(stamp))
                self.end_headers()
                try:
                    self.wfile.write(pixels)
                except (BrokenPipeError, ConnectionResetError):
                    pass

        self.server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
        self.server.daemon_threads = True
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def publish(self, rgb):
        self.latest = (time.monotonic(), rgb.tobytes())

    def close(self):
        self.latest = None
        self.server.shutdown()
        self.server.server_close()


def camera_canvas(frame):
    """Letterbox without cropping; inference and effects use identical 16:9 UVs."""
    height, width = frame.shape[:2]
    scale = min(640 / width, 360 / height)
    w, h = max(1, round(width * scale)), max(1, round(height * scale))
    resized = cv2.resize(frame, (w, h), interpolation=cv2.INTER_AREA)
    canvas = np.zeros((360, 640, 3), dtype=np.uint8)
    x, y = (640 - w) // 2, (360 - h) // 2
    canvas[y:y+h, x:x+w] = resized
    return canvas


class HandTracker:
    """Normalize the CPU Hands and Tasks APIs to (landmarks, label) pairs."""
    def __init__(self, backend, model):
        self.backend = backend
        if backend == 'legacy':
            if not hasattr(mp, 'solutions'):
                raise RuntimeError('CPU Hands requires the supplied compatibility requirements. '
                                   'Replace requirements.txt and click Install / Start controller.')
            self.detector = mp.solutions.hands.Hands(
                static_image_mode=False, max_num_hands=2, model_complexity=1,
                min_detection_confidence=0.6, min_tracking_confidence=0.6)
        else:
            opts = mp.tasks.vision.HandLandmarkerOptions(
                base_options=mp.tasks.BaseOptions(model_asset_path=str(model),
                                                  delegate=mp.tasks.BaseOptions.Delegate.CPU),
                running_mode=mp.tasks.vision.RunningMode.VIDEO, num_hands=2,
                min_hand_detection_confidence=0.6, min_hand_presence_confidence=0.6,
                min_tracking_confidence=0.6)
            self.detector = mp.tasks.vision.HandLandmarker.create_from_options(opts)

    def detect(self, rgb, timestamp):
        if self.backend == 'legacy':
            result = self.detector.process(rgb)
            return [(lm.landmark, labels.classification[0].label)
                    for lm, labels in zip(result.multi_hand_landmarks or [],
                                          result.multi_handedness or [])]
        result = self.detector.detect_for_video(
            mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), timestamp)
        return [(lm, labels[0].category_name)
                for lm, labels in zip(result.hand_landmarks, result.handedness)]

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.detector.close()


def parse_command(text):
    """Accept exactly one recognized command, optionally followed by 'breathing'."""
    text = text.strip().lower()
    if text.endswith(' breathing'):
        text = text[:-10].strip()
    return COMMANDS.get(text)


class PoseFilter:
    def __init__(self):
        self.candidate = 0
        self.current = 0
        self.since = 0.0

    def update(self, candidate, now):
        if candidate != self.candidate:
            self.candidate, self.since = candidate, now
        if now - self.since >= 0.15:
            self.current = candidate
        return self.current

    def reset(self):
        self.candidate = self.current = 0
        self.since = 0.0


def features(landmarks, width, height, was_pinched):
    # Pixel-space ratios avoid distortion from non-square camera images.
    p = np.array([(v.x * width, v.y * height) for v in landmarks])
    palm = max(float(np.linalg.norm(p[5] - p[17])), 12.0)
    ratio = float(np.linalg.norm(p[4] - p[8])) / palm
    pinched = ratio < (0.38 if was_pinched else 0.28)
    # A simple palm-facing classifier; not robust to all rotations/occlusions.
    straight = []
    for base, joint, tip in [(5, 6, 8), (9, 10, 12), (13, 14, 16), (17, 18, 20)]:
        a, b = p[base] - p[joint], p[tip] - p[joint]
        cosine = float(np.dot(a, b)) / max(float(np.linalg.norm(a) * np.linalg.norm(b)), 1e-6)
        straight.append(cosine < -0.65 and np.linalg.norm(p[tip]-p[0]) > 1.12*np.linalg.norm(p[joint]-p[0]))
    # Prioritize a visibly closed fist over accidental thumb/index contact.
    if sum(straight) == 0:
        pose = 3
    elif pinched:
        pose = 1
    elif sum(straight) >= 3:
        pose = 2
    else:
        pose = 0
    center = p[[0, 5, 9, 13, 17]].mean(axis=0)
    x, y = center[0] / width, 1.0 - center[1] / height
    return float(x), float(y), float(np.clip(1-ratio/0.8, 0, 1)), pinched, pose


def voice_worker(args, events, stop):
    # Separate worker: speech decoding cannot block the camera loop.
    try:
        import sounddevice as sd
        from vosk import Model, KaldiRecognizer
        model = Model(str(args.voice_model))
        phrases = list(COMMANDS) + [s+' breathing' for s in ALIASES] + ['[unk]']
        device = args.mic
        rate = int(sd.query_devices(device, 'input')['default_samplerate'])
        recognizer = KaldiRecognizer(model, rate, json.dumps(phrases))
        audio = queue.Queue(maxsize=12)

        def callback(indata, frames, time_info, status):
            if status:
                events.put(('warning', str(status)))
            try:
                audio.put_nowait(bytes(indata))
            except queue.Full:
                pass

        with sd.RawInputStream(samplerate=rate, blocksize=max(512, int(rate*0.05)),
                               device=device, dtype='int16', channels=1, callback=callback):
            print('Microphone ready. Say one style, then pause briefly.')
            while not stop.is_set():
                try:
                    data = audio.get(timeout=0.2)
                except queue.Empty:
                    continue
                samples = np.frombuffer(data, dtype=np.int16).astype(np.float32)/32768.0
                events.put(('rms', float(np.sqrt(np.mean(samples*samples)))))
                if recognizer.AcceptWaveform(data):
                    text = json.loads(recognizer.Result()).get('text', '')
                    if text:
                        events.put(('voice', text))
    except Exception as exc:
        events.put(('warning', 'Voice unavailable: '+str(exc)+'; keyboard still works.'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--camera', type=int, default=0)
    parser.add_argument('--hand', choices=['Left', 'Right'], default='Right',
                        help='MediaPipe label shown on preview, calibrate visually')
    parser.add_argument('--model', type=Path, default=ROOT/'models/hand_landmarker.task')
    parser.add_argument('--voice-model', type=Path, default=ROOT/'models/vosk-model-small-en-us-0.15')
    parser.add_argument('--no-voice', action='store_true')
    parser.add_argument('--list-mics', action='store_true')
    parser.add_argument('--mic', type=int)
    parser.add_argument('--port', type=int, default=9000)
    parser.add_argument('--video-port', type=int, default=9001)
    parser.add_argument('--no-video-feed', action='store_true',
                        help='Disable the clean camera feed for TouchDesigner')
    parser.add_argument('--tracker', choices=['auto', 'legacy', 'tasks'], default='auto')
    parser.add_argument('--self-test', action='store_true',
                        help='Test native hand inference without opening camera or microphone')
    args = parser.parse_args()
    if args.list_mics:
        import sounddevice as sd
        print(sd.query_devices())
        return
    backend = ('legacy' if sys.platform == 'darwin' else 'tasks') if args.tracker == 'auto' else args.tracker
    if backend == 'tasks' and not args.model.is_file():
        parser.error('Missing hand model; click Install / Start controller.')
    print(f'Hand tracker: {backend}, CPU; MediaPipe {mp.__version__}', flush=True)
    if args.self_test:
        with HandTracker(backend, args.model) as detector:
            for timestamp in (1, 34, 67):
                detector.detect(np.zeros((480, 640, 3), dtype=np.uint8), timestamp)
        print('Hand tracker self-test PASSED. Camera and microphone were not opened.', flush=True)
        return
    client = SimpleUDPClient('127.0.0.1', args.port)
    events, stop = queue.Queue(), threading.Event()
    if not args.no_voice:
        threading.Thread(target=voice_worker, args=(args, events, stop), daemon=True).start()
    camera = cv2.VideoCapture(args.camera)
    if not camera.isOpened():
        stop.set()
        raise RuntimeError('Cannot open camera. Check permissions, other apps, and --camera.')
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    camera.set(cv2.CAP_PROP_FPS, 30)
    style, enabled, seq, event_id = 1, True, 0, 0
    command_seq, session = 0, secrets.randbelow(2**30)
    pose_filter = PoseFilter()
    pinched, previous, smoothed = False, None, None
    previous_time, timestamp, speed, rms, audio_time = time.monotonic(), 0, 0.0, 0.0, 0.0
    last_form, last_style, last_active, last_trigger = 0, style, False, 0.0
    print('Preview controls: 1..9 select style; space pauses; q exits.')
    feed = None
    try:
        if not args.no_video_feed:
            try:
                feed = CameraFeed(args.video_port)
                print(f'Clean camera feed ready on localhost port {args.video_port}.', flush=True)
            except OSError as exc:
                print(f'Camera feed unavailable: {exc}. Hand and voice controls still work.', flush=True)
        with HandTracker(backend, args.model) as detector:
            while True:
                ok, frame = camera.read()
                if not ok:
                    raise RuntimeError('Camera stopped delivering frames.')
                frame = cv2.flip(frame, 1)  # Mirror ONCE, before inference and display.
                if not args.no_video_feed:
                    frame = camera_canvas(frame)
                h, w = frame.shape[:2]
                now = time.monotonic()
                dt = max(now-previous_time, 0.001)
                previous_time = now
                while True:
                    try:
                        kind, value = events.get_nowait()
                    except queue.Empty:
                        break
                    if kind == 'rms':
                        rms, audio_time = value, now
                    elif kind == 'warning':
                        print(value)
                    else:
                        command = parse_command(value)
                        print('Heard:', value)
                        client.send_message('/voice', value)
                        if command is not None:
                            command_seq += 1
                            if command >= 0:
                                style, enabled = command, True
                            elif command == -1:
                                enabled = False
                            else:
                                enabled = True
                timestamp = max(timestamp+1, int(now*1000))
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                if feed is not None:
                    feed.publish(rgb)  # Before drawing tracking dots or diagnostic text.
                hands = {}
                for lm, label in detector.detect(rgb, timestamp):
                    hands[label] = lm
                    for p in lm:
                        cv2.circle(frame, (int(p.x*w), int(p.y*h)), 3, (90, 240, 130), -1)
                    cv2.putText(frame, label, (int(lm[0].x*w), int(lm[0].y*h)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
                tracked = args.hand in hands
                other_label = 'Left' if args.hand == 'Right' else 'Right'
                second = other_label in hands
                ox, oy = 0.5, 0.5
                if second:
                    ox, oy, _, _, _ = features(hands[other_label], w, h, False)
                x, y = smoothed if smoothed is not None else (0.5, 0.5)
                strength, form = 0.0, 0
                if tracked:
                    rx, ry, strength, pinched, candidate = features(hands[args.hand], w, h, pinched)
                    alpha = 1-math.exp(-dt/0.055)
                    smoothed = np.array([rx, ry]) if smoothed is None else smoothed+alpha*(np.array([rx, ry])-smoothed)
                    x, y = map(float, smoothed)
                    instantaneous = 0.0 if previous is None else float(np.linalg.norm(smoothed-previous))/dt
                    speed += alpha*(min(instantaneous/2.0, 1.0)-speed)
                    previous = smoothed.copy()
                    form = pose_filter.update(candidate, now)
                else:
                    pinched, previous, smoothed, speed = False, None, None, 0.0
                    pose_filter.reset()
                active = bool(tracked and enabled and form != 0)
                if active and (form != last_form or style != last_style or not last_active) and now-last_trigger >= 0.45:
                    event_id += 1
                    last_trigger = now
                last_form, last_style, last_active = form, style, active
                span = min(math.hypot((x-ox)*w/h, y-oy), 1.0) if second and tracked else 0.0
                if now-audio_time > 0.5:
                    rms = 0.0
                seq += 1
                client.send_message('/state', [seq, style, form, float(x), float(y), float(speed),
                                    strength, int(active), ox, oy, int(second), span, event_id, min(rms*8, 1.0),
                                    int(enabled), command_seq, session])
                cv2.putText(frame, f'{STYLES[style]} | pose {form} | '+('ON' if active else 'idle'),
                            (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
                cv2.imshow('Breathing controller - click here for keyboard controls', frame)
                key = cv2.waitKey(1) & 0xff
                if key == ord('q'):
                    break
                if ord('1') <= key <= ord('9'):
                    style, enabled = key-ord('1'), True
                    command_seq += 1
                if key == ord(' '):
                    enabled = not enabled
                    command_seq += 1
    finally:
        stop.set()
        if feed is not None:
            feed.close()
        camera.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
