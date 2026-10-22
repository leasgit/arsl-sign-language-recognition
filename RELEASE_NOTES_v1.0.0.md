# ArSL Sign Recognition v1.0.0

First Windows desktop release of the Arabic Sign Language letter-recognition application.

## Highlights

- Standalone Windows desktop application; end users do not need Python.
- Live webcam recognition for 32 ArSL alphabet classes.
- MediaPipe hand detection + CNN classification.
- English and Arabic interface modes.
- Word builder with Add Letter, Delete, and Clear controls.
- Manual written-form selection for `ا / أ / إ / آ`, `و / ؤ`, and `ي / ئ`.
- Local camera processing.
- Startup loading screen.
- Custom ArSL application icon.
- Windows installer with Start Menu integration and optional desktop shortcut.

## Installation

Download and run:

`ArSL_Sign_Recognition_Setup.exe`

Follow the setup wizard, then launch **ArSL Sign Recognition** from the Start Menu or desktop shortcut.

## Recommended recognition conditions

For the most reliable predictions:

- Use a white or plain light background behind the hand.
- Use good, even lighting so the hand is clearly visible.
- Keep the full hand visible and reasonably centered in the camera view.

## Current validation

- CNN test accuracy on ArSL2018: 96.78%.
- Macro-average precision / recall / F1: 0.968.
- Controlled webcam evaluation: all 32 classes recognized top-1.
- Packaged application tested on Windows 11 x64.
- Clean-machine installer test completed successfully on a separate Windows laptop; recognition also worked correctly there.

## Known limitations

- Recognizes isolated alphabet signs only; this is not continuous sign-language translation.
- Performance varies with signer, lighting, camera quality, hand position, background, and distance.
- Current testing shows the most reliable performance with a white/plain light background and good lighting.
- The training dataset consists of still images, so webcam conditions introduce a domain shift.
- Arabic orthographic variants such as hamza forms cannot always be inferred from the hand sign and may require user selection.
- The current installer is unsigned, so Windows SmartScreen may show an unrecognized-app warning on some computers.
- Further testing with Arabic Sign Language users and NGO staff is recommended before wider deployment.

## Recommended release test

Before distributing this build, install it on a separate Windows computer with no Python environment and verify startup, camera access, recognition, bilingual UI, written-form selection, shortcuts, and uninstall behavior.
