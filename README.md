# Arabic Sign Language (ArSL) Letter Recognition

AI for Lebanon — Education & Accessibility project. Trains a CNN to classify
Arabic Sign Language alphabet hand-signs from images, and deploys it in a
live webcam demo (using MediaPipe hand detection) that lets you "spell" words
letter by letter in front of your camera.

**Test accuracy: 96.78%** on the ArSL2018 dataset (32 classes, 54,049 images).
**Live webcam: 32/32 letters correctly recognized (top-1)** under controlled
lighting conditions — see the project report for full results and analysis.

## Contents

- `ArSL_Sign_Language_Recognition.ipynb` — full training notebook: data
  loading, preprocessing, CNN architecture, training, and evaluation, with
  inline explanations of each step.
- `webcam_arsl_demo.py` — live webcam demo script using MediaPipe hand
  detection + the trained model.
- `Project_Report.md` — full project write-up (problem statement,
  methodology, results, discussion, reflection).

## Setup

### 1. Get the dataset
This repo does **not** include the dataset (54,049 images, too large for
GitHub). Download it from Mendeley Data:
https://data.mendeley.com/datasets/y7pckrw6z2/1

Unzip it so the folder structure looks like:
```
ArASL_Database_54K_Final/ArASL_Database_54K_Final/<letter>/*.jpg
```
Place that folder alongside the notebook (or update `DATA_DIR` in the
notebook's config cell to point to wherever you put it).

### 2. Install dependencies
```bash
pip install tensorflow pandas numpy matplotlib seaborn scikit-learn nbformat
```

### 3. Run the notebook
Open `ArSL_Sign_Language_Recognition.ipynb` in Jupyter and run all cells.
This trains the model and saves it as `arsl_cnn_model.keras`.

### 4. Try the live webcam demo (optional)
```bash
pip install mediapipe opencv-python
```
Download the MediaPipe hand landmark model:
https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task

Save it as `hand_landmarker.task` in the same folder as
`webcam_arsl_demo.py`, along with the trained `arsl_cnn_model.keras`, then
run:
```bash
python webcam_arsl_demo.py
```

## Results summary

| Metric | Value |
|---|---|
| Test accuracy | 96.78% |
| Test loss | 0.1403 |
| Macro-average precision/recall/F1 | 0.968 |
| Live webcam letters correctly recognized (top-1) | 32/32 |

See `Project_Report.md` for full methodology, per-class results, confusion
matrix analysis, and discussion of the live-vs-offline domain gap.

## Dataset citation

Latif, G., Alghazo, J., Mohammad, N., AlKhalaf, R., & AlKhalaf, R. (2019).
ArSL2018: Arabic Sign Language dataset for Arabic sign language recognition.
Mendeley Data. https://data.mendeley.com/datasets/y7pckrw6z2/1
