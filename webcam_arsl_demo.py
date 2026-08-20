"""
Live ArSL Letter Recognition — Webcam Demo
============================================
Uses MediaPipe's HandLandmarker to detect and crop your hand from the
webcam feed, then feeds the crop into your trained ArSL CNN to predict
the Arabic sign language letter in real time.

Controls (while the webcam window is focused):
    SPACE     -> confirm the current predicted letter and add it to the spelled word
    BACKSPACE -> remove the last letter from the spelled word
    C         -> clear the spelled word
    Q or ESC  -> quit

ONE-TIME SETUP
--------------
1. Install dependencies:
       pip install mediapipe opencv-python tensorflow numpy

   NOTE: install ONLY `opencv-python` — do not also separately install
   `opencv-contrib-python`, mediapipe already brings a compatible OpenCV
   build in as a dependency, and mixing packages can cause import conflicts.

2. Download the MediaPipe hand landmark model file (one-time, ~lightweight):
       https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
   Save it in the SAME folder as this script, named exactly:
       hand_landmarker.task

3. Make sure `arsl_cnn_model.keras` (saved by the training notebook) is
   also in the same folder as this script.

Then just run:
       python webcam_arsl_demo.py
"""

import os
import time
import cv2
import numpy as np
import tensorflow as tf
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import (
    HandLandmarker,
    HandLandmarkerOptions,
    RunningMode,
)

# ---------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------
MODEL_PATH = "arsl_cnn_model.keras"
HAND_MODEL_PATH = "hand_landmarker.task"
IMG_SIZE = 64
CONFIDENCE_THRESHOLD = 0.40   # below this, we show "uncertain" instead of guessing
CROP_MARGIN = 0.6             # extra padding around the detected hand box (fraction of box size)

# Class order MUST match the alphabetical folder order used during training
# (this is what `sorted(os.listdir(DATA_DIR))` produced in the notebook)
CLASS_NAMES = [
    'ain', 'al', 'aleff', 'bb', 'dal', 'dha', 'dhad', 'fa', 'gaaf', 'ghain',
    'ha', 'haa', 'jeem', 'kaaf', 'khaa', 'la', 'laam', 'meem', 'nun', 'ra',
    'saad', 'seen', 'sheen', 'ta', 'taa', 'thaa', 'thal', 'toot', 'waw',
    'ya', 'yaa', 'zay'
]
# NOTE: double check this list against `classes` printed in your notebook
# (cell under "4. Train / Validation / Test Split") — it MUST match exactly,
# in the same order, or predictions will be labeled wrong even if the
# model itself is correct.

# ---------------------------------------------------------------------
# Sanity checks
# ---------------------------------------------------------------------
if not os.path.isfile(MODEL_PATH):
    raise FileNotFoundError(
        f"Could not find '{MODEL_PATH}'. Copy the .keras model saved by "
        f"the training notebook into this folder first."
    )
if not os.path.isfile(HAND_MODEL_PATH):
    raise FileNotFoundError(
        f"Could not find '{HAND_MODEL_PATH}'. Download it from:\n"
        f"https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
        f"hand_landmarker/float16/1/hand_landmarker.task\n"
        f"and place it in this folder."
    )

# ---------------------------------------------------------------------
# Load models
# ---------------------------------------------------------------------
print("Loading CNN model...")
cnn_model = tf.keras.models.load_model(MODEL_PATH)

print("Loading MediaPipe HandLandmarker...")
hand_options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=HAND_MODEL_PATH),
    running_mode=RunningMode.IMAGE,  # fresh detection every frame — no frame-to-frame
                                       # tracking, which was causing landmark drift and
                                       # wildly oversized/mislocated bounding boxes
    num_hands=1,
    min_hand_detection_confidence=0.6,
)
landmarker = HandLandmarker.create_from_options(hand_options)


def get_hand_bbox(hand_landmarks, frame_width, frame_height):
    """Compute a padded, SQUARE bounding box (in PIXEL coords) around detected hand
    landmarks. We convert to pixel coordinates FIRST, then build the square box —
    doing it in normalized [0,1] coordinates would produce a non-square box once
    converted to pixels, since webcam frames aren't square (e.g. 1280x720).
    A square, undistorted crop matters because the training images were square;
    resizing a stretched rectangle to 64x64 would distort the hand shape in a way
    the model never saw during training.

    Also caps the box size at a fraction of the frame so a bad/noisy landmark
    detection can't produce a runaway box that swallows your face/background."""
    xs_px = [lm.x * frame_width for lm in hand_landmarks]
    ys_px = [lm.y * frame_height for lm in hand_landmarks]
    x_min, x_max = min(xs_px), max(xs_px)
    y_min, y_max = min(ys_px), max(ys_px)

    cx = (x_min + x_max) / 2.0
    cy = (y_min + y_max) / 2.0
    box_w = x_max - x_min
    box_h = y_max - y_min
    side = max(box_w, box_h) * (1.0 + CROP_MARGIN)

    # Safety cap: a real hand crop shouldn't need to exceed ~70% of the shorter
    # frame dimension. If it does, the landmarks are almost certainly noisy/bad.
    max_side = 0.80 * min(frame_width, frame_height)
    side = min(side, max_side)

    x_min = cx - side / 2.0
    x_max = cx + side / 2.0
    y_min = cy - side / 2.0
    y_max = cy + side / 2.0

    # If the box would extend past a frame edge, SHIFT it inward (keeping it
    # square) rather than clipping only the exceeding side — clipping only one
    # side (e.g. when the hand is near the right edge) breaks the square shape
    # and re-introduces the aspect-ratio distortion we're trying to avoid.
    if x_min < 0:
        x_max -= x_min
        x_min = 0
    if x_max > frame_width:
        x_min -= (x_max - frame_width)
        x_max = frame_width
    if y_min < 0:
        y_max -= y_min
        y_min = 0
    if y_max > frame_height:
        y_min -= (y_max - frame_height)
        y_max = frame_height

    # final clamp in case the box is still larger than the frame itself
    x_min = max(0, int(x_min))
    x_max = min(frame_width, int(x_max))
    y_min = max(0, int(y_min))
    y_max = min(frame_height, int(y_max))

    return (x_min, y_min, x_max, y_max)


def predict_letter(hand_crop_bgr):
    """Preprocess a cropped hand image and run it through the CNN.
    Returns the top-1 (letter, confidence) plus the full sorted top-5,
    the exact preprocessed 64x64 array fed to the model (for debug saving),
    and the raw crop (for debug saving)."""
    gray = cv2.cvtColor(hand_crop_bgr, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (IMG_SIZE, IMG_SIZE))
    normalized = resized.astype(np.float32) / 255.0
    input_tensor = normalized[np.newaxis, ..., np.newaxis]  # (1, 64, 64, 1)
    preds = cnn_model.predict(input_tensor, verbose=0)[0]

    top5_idx = np.argsort(preds)[::-1][:5]
    top5 = [(CLASS_NAMES[i], float(preds[i])) for i in top5_idx]

    idx = int(top5_idx[0])
    confidence = float(preds[idx])
    return CLASS_NAMES[idx], confidence, top5, resized


# ---------------------------------------------------------------------
# Webcam loop
# ---------------------------------------------------------------------
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Could not open webcam. Check camera permissions / index.")

spelled_word = ""
last_letter = None
start_time = time.time()
last_debug_print = 0.0
DEBUG_PRINT_INTERVAL = 0.75  # seconds between console debug prints (avoid flooding)

print("\nStarting webcam. Press SPACE to add the current letter, "
      "BACKSPACE to remove last, C to clear, Q/ESC to quit.\n")
print("Debug info (top-5 predictions) will print to this console periodically.")
print("The exact image the model sees is also saved to 'debug_model_input.png'")
print("and the raw color crop (before grayscale/resize) to 'debug_raw_crop.png'")
print("after each frame with a detected hand — open these to visually check")
print("what the model is actually looking at.\n")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame from webcam.")
            break

        # IMPORTANT: hand detection + classification run on the RAW (unflipped)
        # frame, matching the orientation of the training photos. We only
        # mirror a SEPARATE copy for on-screen display, so it feels natural
        # to look at, without corrupting what the model actually sees.
        frame_height, frame_width = frame.shape[:2]

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        result = landmarker.detect(mp_image)  # fresh per-frame detection, no tracking

        # Build the mirrored frame used ONLY for display
        display_frame = cv2.flip(frame, 1)

        display_text = "No hand detected"
        last_letter = None

        if result.hand_landmarks:
            hand_landmarks = result.hand_landmarks[0]
            x1, y1, x2, y2 = get_hand_bbox(hand_landmarks, frame_width, frame_height)

            # Map the box from raw-frame coords into mirrored-display coords
            disp_x1 = frame_width - x2
            disp_x2 = frame_width - x1
            cv2.rectangle(display_frame, (disp_x1, y1), (disp_x2, y2), (0, 255, 0), 2)

            if x2 > x1 and y2 > y1:
                hand_crop = frame[y1:y2, x1:x2]  # crop from the RAW frame, not the mirrored one
                letter, confidence, top5, model_input_img = predict_letter(hand_crop)

                if confidence >= CONFIDENCE_THRESHOLD:
                    display_text = f"{letter} ({confidence:.0%})"
                    last_letter = letter
                else:
                    display_text = f"uncertain ({confidence:.0%})"

                now = time.time()
                if now - last_debug_print >= DEBUG_PRINT_INTERVAL:
                    last_debug_print = now
                    top5_str = "  ".join(f"{name}:{conf:.1%}" for name, conf in top5)
                    print(f"[bbox px]=({x1},{y1})-({x2},{y2})  "
                          f"crop_size={x2-x1}x{y2-y1}  |  top5: {top5_str}")
                    cv2.imwrite("debug_model_input.png", (model_input_img).astype(np.uint8))
                    cv2.imwrite("debug_raw_crop.png", hand_crop)

        # overlay prediction
        cv2.putText(display_frame, display_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX,
                    1.0, (0, 255, 0), 2, cv2.LINE_AA)

        # overlay spelled word so far
        cv2.putText(display_frame, f"Word: {spelled_word}", (20, frame_height - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 0), 2, cv2.LINE_AA)

        cv2.putText(display_frame, "SPACE=add  BACKSPACE=del  C=clear  Q=quit",
                    (20, frame_height - 60), cv2.FONT_HERSHEY_SIMPLEX,
                    0.55, (200, 200, 200), 1, cv2.LINE_AA)

        cv2.imshow("ArSL Letter Recognition", display_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:  # q or ESC
            break
        elif key == 32:  # SPACE
            if last_letter is not None:
                spelled_word += f"[{last_letter}]"
        elif key == 8:  # BACKSPACE
            # remove the last "[letter]" token, not just one character
            if spelled_word.endswith("]"):
                spelled_word = spelled_word[:spelled_word.rfind("[")]
        elif key == ord('c'):
            spelled_word = ""

finally:
    cap.release()
    cv2.destroyAllWindows()
    landmarker.close()
    print(f"\nFinal spelled word: {spelled_word}")
