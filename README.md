# Arabic Sign Language (ArSL) Letter Recognition

A Windows desktop application and research project for recognizing isolated Arabic Sign Language alphabet signs from a webcam feed. The app uses a CNN trained on the ArSL2018 dataset together with MediaPipe hand detection, and lets users build written Arabic words letter by letter.

## For end users

The easiest way to use the project is the Windows installer. No Python setup or model training is required.

### Install on Windows

1. Download `ArSL_Sign_Recognition_Setup.exe` from the latest GitHub Release.
2. Double-click the installer and follow the setup wizard.
3. Optionally create a desktop shortcut during installation.
4. Open **ArSL Sign Recognition** from the Start Menu or desktop.
5. Allow camera access if Windows asks for permission.

The app shows a loading screen while the recognition model starts, then opens the webcam interface. It supports English and Arabic interface text.

### For best recognition

For the most reliable predictions:

- Use a **white or plain light background** behind the hand.
- Use **good, even lighting** so the hand is clearly visible to the camera.
- Keep the full hand visible and reasonably centered in the camera view.

> The current packaged build has been tested on Windows 11 x64. It should be tested on the exact NGO/target machines before deployment.

## What the app does

- Recognizes 32 Arabic Sign Language alphabet classes from a webcam.
- Displays the detected Arabic letter and confidence score.
- Lets the user add, delete, and clear letters to build a word.
- Provides manual written-form choices for orthographic variants such as `ا / أ / إ / آ`, `و / ؤ`, and `ي / ئ`.
- Supports English and Arabic interface modes.
- Processes camera frames locally on the computer.

## Important limitations

This is an **isolated-letter recognition prototype**, not a complete Arabic Sign Language translator.

- It recognizes one alphabet sign at a time; it does not recognize continuous signing, full words, grammar, facial expressions, or sentences.
- Accuracy can vary with lighting, camera quality, background, hand position, distance, and signer differences.
- In current testing, recognition is most reliable with a white/plain light background and good lighting.
- The CNN was trained on the ArSL2018 image dataset, so real webcam conditions can differ from the training data.
- Some written Arabic forms cannot be determined from the hand sign alone. For example, the recognized alef sign may need to be written as `ا`, `أ`, `إ`, or `آ`, so the user chooses the intended form in the interface.
- Dataset/test accuracy should not be interpreted as guaranteed real-world accuracy.
- Further testing with Arabic Sign Language users and NGO staff is recommended before broader deployment.

## Model results

| Metric | Value |
|---|---:|
| Test accuracy | 96.78% |
| Test loss | 0.1403 |
| Macro-average precision / recall / F1 | 0.968 |
| Controlled live evaluation | 32/32 classes recognized top-1 |

The live result above was obtained under controlled conditions and is not a guarantee of performance for every signer or environment. See `Project_Report.md` for the full methodology and evaluation discussion.

## Project structure

- `app.py` — PySide6 desktop interface, bilingual UI, webcam display, word building, and written-form selector.
- `recognition.py` — MediaPipe hand detection and CNN inference pipeline.
- `run_app.py` — application entry point with startup loading screen and packaged-resource handling.
- `build_windows.ps1` — builds the standalone Windows application with PyInstaller.
- `installer.iss` — Inno Setup configuration for the Windows installer.
- `build_installer.ps1` — compiles the final Windows installer.
- `ArSL_Sign_Language_Recognition.ipynb` — training and evaluation notebook.
- `webcam_arsl_demo.py` — original development webcam demo.
- `Project_Report.md` — detailed project report.

## Run from source

The trained CNN file and MediaPipe hand-landmarker file are not stored in the repository because they are large binaries.

### 1. Install runtime dependencies

```bash
pip install -r requirements.txt
```

### 2. Add the required model files

Place these files in the repository root:

```text
arsl_cnn_model.keras
hand_landmarker.task
```

The MediaPipe hand-landmarker model can be downloaded from:

https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task

### 3. Start the desktop app

```bash
python run_app.py
```

## Train the CNN

The dataset is not included in this repository. Download ArSL2018 from Mendeley Data:

https://data.mendeley.com/datasets/y7pckrw6z2/1

Expected folder structure:

```text
ArASL_Database_54K_Final/
└── ArASL_Database_54K_Final/
    └── <letter>/
        └── *.jpg
```

Install the training dependencies:

```bash
pip install -r requirements-training.txt
```

Then open `ArSL_Sign_Language_Recognition.ipynb` and run the notebook. It saves the trained model as `arsl_cnn_model.keras`.

## Build the Windows application

With the model files present in the repository root:

```powershell
.\build_windows.ps1
```

The standalone application is created under:

```text
dist\ArSL Sign Recognition\
```

## Build the Windows installer

Install Inno Setup 6, then run:

```powershell
.\build_installer.ps1
```

The distributable installer is created at:

```text
installer_output\ArSL_Sign_Recognition_Setup.exe
```

Before publishing a release, test this installer on a separate Windows computer that does not have Python installed.

## Privacy

Recognition is designed to run locally. Webcam frames are processed on the user's computer by MediaPipe and the CNN model; the packaged desktop application does not require a cloud recognition service.

## Dataset citation

Latif, G., Alghazo, J., Mohammad, N., AlKhalaf, R., & AlKhalaf, R. (2019). *ArSL2018: Arabic Sign Language dataset for Arabic sign language recognition*. Mendeley Data. https://data.mendeley.com/datasets/y7pckrw6z2/1
