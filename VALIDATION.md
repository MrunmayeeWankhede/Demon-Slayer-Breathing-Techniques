# Validation — 6 September 2026

This is an automatic TouchDesigner project builder plus a controller launcher. It is not a locally tested `.toe` file.

Passed in the build environment:

- Python syntax compilation for all supplied Python sources.
- Both effect and finish shaders compiled to SPIR-V with the Khronos glslang WebAssembly compiler. Compatibility declarations supplied TouchDesigner's shader inputs, output helper, and uniform bindings. This confirms shader-language compilation, not TouchDesigner's own GPU pipeline.
- A real UDP OSC packet round trip through `python-osc` with the 17-field controller protocol.
- Controller logic checks with simulated TouchDesigner parameters: manual style selection survives ordinary camera updates; a new voice/keyboard command takes precedence; choosing demo survives continuing camera packets; disconnect turns emission off; a restarted sender reconnects; stale/invalid packets are ignored; pause works.
- Nine style tables and 27 form labels are present.
- Both official model downloads completed and their SHA-256 hashes were recorded. The launcher verifies these before using downloaded bytes.
- Vosk loaded the English model and decoded one second of silent PCM to an empty transcript. This does not measure speech recognition accuracy.

Not completed here:

- TouchDesigner installation/build execution: this environment runs Linux and has no TouchDesigner.
- GPU rendering or visual layout inspection of the generated TouchDesigner interface.
- Live hand inference with real camera images. The initial MediaPipe runtime could not load without EGL; the patched version passed blank-frame tests below.
- Physical webcam, microphone, handedness, pose accuracy, speech accuracy, and latency testing.
- Native Windows `.cmd`, macOS `.command`, and Tk launcher interaction tests.

The shader and control checks reduce implementation risk but do not establish end-to-end compatibility. The installer preserves a partial component and prints a named error if the local TouchDesigner API differs. Shader Info DATs and `controller.log` support diagnosis on the target machine.

Original build dependencies observed in Linux: Python 3.12.13, mediapipe 1.0.1, opencv-contrib-python 5.0.0.93, numpy 2.3.5, python-osc 1.10.2, vosk 0.3.45, sounddevice 0.5.6. The later Mac compatibility patch below replaces the core dependency selection. This is not a complete cross-platform lockfile.

## Certificate fix — 7 September 2026

The launcher now obtains the certifi CA bundle path from its private Python environment and adds it to a default TLS context. Certificate-chain and hostname verification remain enabled. A real hand-model download with the patched function passed its expected SHA-256 check, and the speech-model server responded successfully over verified HTTPS. Existing package installations can be reused by replacing only launcher.py. certifi is now an explicit requirement for fresh installations. This fix has been tested in the build environment, not on the user’s Mac.

## Mac native-crash compatibility patch — 7 September 2026

The user's log reached microphone initialization, then aborted inside MediaPipe's `DrishtiMetalHelper` from `TensorsToDetectionsCalculator::Open`. This points to native graph initialization rather than a Python exception or the earlier camera permission failure; the exact upstream cause has not been confirmed.

The patch pins MediaPipe 0.10.21, OpenCV-contrib 4.11.0.86, NumPy 1.26.4 and JAX/JAXLIB 0.4.35. On Mac it selects `mp.solutions.hands.Hands`, whose bundled graph is `hand_landmark_tracking_cpu.binarypb`. Other platforms use Tasks with an explicit CPU delegate. Both adapters return the same landmark/hand-label pairs; the OSC packet and TouchDesigner project are unchanged.

This is an older API compatibility workaround. [The official MediaPipe distribution](https://pypi.org/project/mediapipe/0.10.21/) provides Python 3.11/3.12 macOS universal2 wheels and states that legacy solutions are provided as-is. The patch is not an assertion that a specific upstream regression has been proven or that macOS execution was tested here.

Before each controller start, a separate subprocess creates the selected tracker and processes three blank frames. A native abort fails this test without opening camera/microphone; the launcher remains available to show the diagnostic. Passing it establishes initialization and empty-frame inference only, not hand recognition accuracy or hardware capture.

Patch verification in Linux/Python 3.12: the pinned packages installed into an isolated environment, `pip check` reported no broken requirements, and both legacy CPU Hands and Tasks CPU processed three blank frames and exited successfully. The legacy adapter preserved 21 landmark objects and the Right label in a synthetic result check and handled an empty result. Both modified Python sources passed syntax compilation. Physical hand detection and macOS execution remain unverified.

## Camera-view add-on — 7 September 2026

Adds a loopback camera-frame server to bridge.py and a separate self-contained ADD_CAMERA_VIEW.py installer. See CAMERA_VIEW.md for setup, verification, and limitations. The existing effect and control nodes remain in place. The clean compositor reads the trails texture before the original UI stage mask, so the full frame is available. Hand inference uses the same letterboxed camera canvas as the clean view to keep coordinates aligned. The server publishes pixels before drawing the preview dots.

Verification: real local HTTP transport and background reader round trip with synthetic RGB frames; Script TOP callback adapter with a stand-in texture object; camera letterboxing, channel and vertical orientation, stale-frame rejection; Python syntax compilation; capture shader GLSL-to-SPIR-V compilation. TouchDesigner installation, Mac live video, visual appearance and recording remain untested here.
