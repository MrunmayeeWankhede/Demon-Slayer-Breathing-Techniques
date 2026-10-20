"""Script TOP callbacks: nonblocking upload of the latest local camera frame."""
import threading
import time
import urllib.request
import numpy as np

_reader = None


class Reader:
    def __init__(self):
        self.stop = threading.Event()
        self.latest = None
        self.message = 'Waiting for camera feed; restart the updated controller.'
        self.thread = threading.Thread(target=self.loop, daemon=True, name='BreathingCameraReader')
        self.thread.start()

    def loop(self):
        # This worker performs no TouchDesigner API calls.
        client = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        while not self.stop.is_set():
            started = time.monotonic()
            try:
                with client.open('http://127.0.0.1:9001/frame', timeout=0.6) as response:
                    payload = response.read(640 * 360 * 3 + 1)
                if len(payload) != 640 * 360 * 3:
                    raise ValueError('Unexpected camera frame size')
                pixels = np.frombuffer(payload, dtype=np.uint8).reshape(360, 640, 3)
                # OpenCV row 0 is the top; TOP texture row 0 is the bottom.
                pixels = np.ascontiguousarray(pixels[::-1])
                self.latest = (time.monotonic(), pixels)
                self.message = 'Camera feed connected'
            except Exception:
                self.message = 'Waiting for camera feed; restart the updated controller.'
                self.stop.wait(0.25)
            self.stop.wait(max(0, 1 / 30 - (time.monotonic() - started)))


def shutdown(scriptOp):
    global _reader
    if _reader is not None:
        _reader.stop.set()
    _reader = None


def onCook(scriptOp):
    global _reader
    if _reader is None or not _reader.thread.is_alive():
        _reader = Reader()
    reader = _reader
    latest = reader.latest
    online = latest is not None and time.monotonic() - latest[0] < 1
    scriptOp.store('camera_online', online)
    scriptOp.store('camera_status', reader.message if online else 'Waiting for camera feed; restart the updated controller.')
    if online:
        scriptOp.copyNumpyArray(latest[1])
    else:
        scriptOp.copyNumpyArray(np.zeros((360, 640, 3), dtype=np.uint8))
    return
