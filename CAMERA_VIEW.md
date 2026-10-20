# Show yourself with your breathing effects

This add-on places your clean webcam video behind the effects in a separate **Camera + effects** window. It excludes green tracking dots and interface buttons. The existing controller continues to capture the camera; TouchDesigner receives the same feed locally.

## Install on your working setup

1. Close the Breathing Studio controller window.
2. Copy this download's `bridge.py` into your existing **Downloads → BreathingStudio** folder. Choose **Replace**. Replace only this file; keep your existing launcher, requirements, models, and saved project.
3. Open your existing `START_MAC.command`, then click **Install / Start controller**. No new Python packages are required beyond the working Mac compatibility patch. Look for **Clean camera feed ready on localhost port 9001**.
4. Open your working Breathing Studio project in TouchDesigner. Open **Dialogs → Textport**, paste this line, and press Enter:

```python
p = ui.chooseFile(); exec(compile(open(p, encoding='utf-8').read(), p, 'exec')) if p else None
```

5. Select **ADD_CAMERA_VIEW.py** from the extracted add-on folder. It is self-contained; it can stay in that folder. A **Breathing Studio - Camera + effects** window opens.
6. In the original control interface, choose **Camera + voice**, show your controlling hand, and say “water.” Position yourself so the camera sees both your face and hands. Click **Save project** to preserve the add-on in your `.toe`.

Use the new **Camera view** button near the top right of the control interface to reopen the clean window. **Video: on/off** changes its camera background. The camera preview still shows tracking dots for calibration; the clean effects window does not.

## Record on your Mac

- Bring the **Camera + effects** window to the front.
- Press **Shift–Command–5** and choose **Record Selected Portion**.
- Drag the recording rectangle around the image area, excluding the window title bar and other windows.
- Under **Options → Microphone**, select your microphone if you want your spoken commands included. Otherwise choose None.
- Click **Record**. Perform your breathing styles. Click the menu-bar Stop button when finished.
- The recording normally saves to Desktop unless you choose another location under Options.

[Apple’s recording instructions](https://support.apple.com/en-us/102618).

This is a landscape camera view. A 4:3 camera receives side bars to preserve its proportions and full field of view. The feed is 640×360 for responsiveness; enlarging it will not add camera detail. Effects draw over the video, including over your body when they overlap; this add-on does not perform person segmentation or depth occlusion. Camera and tracking updates can differ by a few frames; it does not promise frame-exact synchronization.

## If something looks wrong

- **Effects but no face:** read the new camera-feed status in the control interface. Confirm **Video: on**, that the updated controller is running, and that its log says the clean feed is ready. Keep TouchDesigner's timeline playing.
- **Port 9001 already in use:** close any older controller instance and start one controller. Do not change the port unless you also update the add-on's receiver.
- **Upside-down camera:** select the BreathingStudio component, open its custom **Camera view** parameter page, and enable **Flip camera vertically**.
- **Effects idle:** choose Camera + voice, check the controlling Right/Left label, and show an open palm, pinch, or fist.
- **Shader error:** inspect the `capture_compile` Info DAT inside BreathingStudio and send its message.
- **Add-on error:** copy the full Textport error. The installer preserves the existing project and any partially added nodes; running it again updates its own named nodes.
- **Want the former controller framing:** the command-line option `--no-video-feed` restores its original camera framing and disables video transfer.

## Validation and limits

Tested in Linux: the real localhost camera server and background reader transferred synthetic RGB frames; the Script TOP callback adapter preserved colors and vertical orientation; stale frames were rejected; letterboxing preserved a 4:3 field of view. Modified Python sources passed compilation. The capture shader compiled to SPIR-V with TouchDesigner compatibility declarations.

Not tested here: the actual TouchDesigner add-on, Mac camera capture, rendered appearance, recording audio, and live synchronization. Your working Mac CPU tracker and certificate fix are retained. This add-on uses the documented [Script TOP NumPy upload API](https://docs.derivative.ca/ScriptTOP_Class).

Video is kept in memory and served only on this computer's loopback interface (127.0.0.1:9001). It is not recorded until you start screen recording. Speech recognition and hand inference remain local.
