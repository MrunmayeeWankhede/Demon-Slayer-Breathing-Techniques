# Breathing Studio

A Demon Slayer-inspired TouchDesigner interface controlled by your hands and voice. Say a breathing style, then use a pinch, open palm, or fist to change its visual form. Moving your hand moves the effect; moving faster increases its intensity.

<img src="https://i.redd.it/wgoilgst8tzd1.jpeg" alt="Alt Text" width="450">

The project includes nine styles and 27 named variations, a mouse demo, offline speech recognition, and an optional camera view that puts you behind the effects for recording.

## Styles and controls

**Flame · Water · Mist · Stone · Love · Wind · Serpent · Insect · Sound**

“Fire” also selects Flame. Say one style at a time and pause briefly; phrases such as “water breathing” work too.

| Input | Action |
| --- | --- |
| Pinch thumb and index | Form 1 |
| Open palm | Form 2 |
| Closed fist | Form 3 |
| Move controlling hand | Move the effect |
| Spread both hands apart | Adjust applicable effect sizes |
| Say “stop” / “start” | Pause / resume |
| Preview keys 1–9 | Select a style |
| Preview Space / Q | Pause / quit |

The gestures are custom controls. They are not canonical hand signs, and the visuals are procedural interpretations rather than anime footage.

## Run it

You need TouchDesigner on macOS or Windows, Python **3.11 or 3.12** with Tk support, a webcam, and optionally a microphone. The Python installation is separate from TouchDesigner's bundled interpreter.

1. Download this repository using **Code → Download ZIP**, then extract it, or clone it.
2. Open TouchDesigner and choose **Dialogs → Textport**. Run:

   ```python
   p = ui.chooseFile(); exec(compile(open(p, encoding='utf-8').read(), p, 'exec')) if p else None
   ```

3. Select `INSTALL_IN_TOUCHDESIGNER.py`. It builds the interface automatically. You can try **Mouse demo** immediately.
4. Open `START_MAC.command` on Mac or `START_WINDOWS.cmd` on Windows. Click **Install / Start controller**. The launcher installs dependencies in `.venv` and downloads the models with checksum verification.
5. Allow camera and microphone access when prompted. Select **Camera + voice** in the TouchDesigner interface. Match the controlling hand selection to the Right/Left label in the preview.
6. Click **Save project** to create your `.toe` file.

If the Mac launcher does not open as a script, run `bash START_MAC.command` from Terminal in the extracted project folder.

The repository contains the project builder, not a prebuilt `.toe`. Detailed setup and troubleshooting are in [START_HERE.md](START_HERE.md).

## Include yourself in the video

With the controller running and your project open, run the same Textport line and select `ADD_CAMERA_VIEW.py`. It adds a separate **Camera + effects** window, using the controller's clean camera feed without the green tracking dots.

On Mac, use **Shift–Command–5 → Record Selected Portion** to record that window. See [CAMERA_VIEW.md](CAMERA_VIEW.md) for installation, microphone recording, and troubleshooting. If you cloned this complete repository, the updated `bridge.py` is already included; you do not need to copy it from another patch.

## How it works

- `bridge.py` runs MediaPipe hand tracking and Vosk speech recognition. It sends control values to TouchDesigner over OSC at `127.0.0.1:9000`.
- `launcher.py` manages the Python environment, model downloads, device settings, and startup inference test.
- `source/` contains the readable TouchDesigner builder, control logic, shaders, and camera-view add-on.
- `INSTALL_IN_TOUCHDESIGNER.py` and `ADD_CAMERA_VIEW.py` embed the source assets so the generated project can be saved without external shader dependencies.
- The optional camera view receives the latest clean frame from `127.0.0.1:9001/frame`.

After installation, hand tracking and speech recognition run locally. The controller does not save camera video or microphone audio. Its diagnostic log includes recognized commands. Downloaded models, virtual environments, settings, logs, and recordings are excluded from Git.

## Status

The base interface and Mac hand/voice controller were reported working during development. The camera-view add-on passed synthetic frame-transfer and shader checks, but its live Mac rendering has not been confirmed. [VALIDATION.md](VALIDATION.md) records the checks and their limits.

The Mac compatibility setup pins MediaPipe 0.10.21 and uses its legacy CPU Hands pipeline. This avoids the native Metal initialization crash encountered during setup. It is a compatibility workaround, not a guarantee for every Mac or future dependency version.

This is an unofficial fan made project. No anime footage, images, or audio are bundled. See [THIRD_PARTY.md](THIRD_PARTY.md) for dependencies and attribution.
