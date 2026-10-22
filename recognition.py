from dataclasses import dataclass

import cv2
import mediapipe as mp
import numpy as np
import tensorflow as tf
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import (
    HandLandmarker,
    HandLandmarkerOptions,
    RunningMode,
)


IMG_SIZE = 64
CROP_MARGIN = 0.6

CLASS_NAMES = [
    "ain", "al", "aleff", "bb", "dal", "dha", "dhad", "fa", "gaaf", "ghain",
    "ha", "haa", "jeem", "kaaf", "khaa", "la", "laam", "meem", "nun", "ra",
    "saad", "seen", "sheen", "ta", "taa", "thaa", "thal", "toot", "waw",
    "ya", "yaa", "zay",
]

# User-facing forms. Ambiguous written forms such as hamza variants are
# selected in the interface before the user adds the letter to the word.
ARABIC_LABELS = {
    "ain": "ع",
    "al": "ال",
    "aleff": "ا",
    "bb": "ب",
    "dal": "د",
    "dha": "ظ",
    "dhad": "ض",
    "fa": "ف",
    "gaaf": "ق",
    "ghain": "غ",
    "ha": "ه",
    "haa": "ح",
    "jeem": "ج",
    "kaaf": "ك",
    "khaa": "خ",
    "la": "لا",
    "laam": "ل",
    "meem": "م",
    "nun": "ن",
    "ra": "ر",
    "saad": "ص",
    "seen": "س",
    "sheen": "ش",
    "ta": "ط",
    "taa": "ت",
    "thaa": "ث",
    "thal": "ذ",
    "toot": "ة",
    "waw": "و",
    "ya": "ي",
    "yaa": "ي",
    "zay": "ز",
}


@dataclass
class Prediction:
    class_name: str
    arabic: str
    confidence: float
    bbox: tuple[int, int, int, int]


class ArSLRecognizer:
    def __init__(self, model_path: str, hand_model_path: str):
        self.model = tf.keras.models.load_model(model_path)

        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=hand_model_path),
            running_mode=RunningMode.IMAGE,
            num_hands=1,
            min_hand_detection_confidence=0.6,
        )
        self.landmarker = HandLandmarker.create_from_options(options)

    def predict(self, frame_bgr) -> Prediction | None:
        frame_height, frame_width = frame_bgr.shape[:2]

        rgb_frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        result = self.landmarker.detect(mp_image)

        if not result.hand_landmarks:
            return None

        x1, y1, x2, y2 = self._get_hand_bbox(
            result.hand_landmarks[0], frame_width, frame_height
        )

        if x2 <= x1 or y2 <= y1:
            return None

        hand_crop = frame_bgr[y1:y2, x1:x2]
        gray = cv2.cvtColor(hand_crop, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, (IMG_SIZE, IMG_SIZE))
        normalized = resized.astype(np.float32) / 255.0
        input_tensor = normalized[np.newaxis, ..., np.newaxis]

        predictions = self.model(input_tensor, training=False).numpy()[0]
        index = int(np.argmax(predictions))
        class_name = CLASS_NAMES[index]
        confidence = float(predictions[index])

        return Prediction(
            class_name=class_name,
            arabic=ARABIC_LABELS[class_name],
            confidence=confidence,
            bbox=(x1, y1, x2, y2),
        )

    @staticmethod
    def _get_hand_bbox(hand_landmarks, frame_width, frame_height):
        xs_px = [landmark.x * frame_width for landmark in hand_landmarks]
        ys_px = [landmark.y * frame_height for landmark in hand_landmarks]

        x_min, x_max = min(xs_px), max(xs_px)
        y_min, y_max = min(ys_px), max(ys_px)

        center_x = (x_min + x_max) / 2.0
        center_y = (y_min + y_max) / 2.0
        box_width = x_max - x_min
        box_height = y_max - y_min

        side = max(box_width, box_height) * (1.0 + CROP_MARGIN)
        side = min(side, 0.80 * min(frame_width, frame_height))

        x_min = center_x - side / 2.0
        x_max = center_x + side / 2.0
        y_min = center_y - side / 2.0
        y_max = center_y + side / 2.0

        if x_min < 0:
            x_max -= x_min
            x_min = 0
        if x_max > frame_width:
            x_min -= x_max - frame_width
            x_max = frame_width
        if y_min < 0:
            y_max -= y_min
            y_min = 0
        if y_max > frame_height:
            y_min -= y_max - frame_height
            y_max = frame_height

        x_min = max(0, int(x_min))
        x_max = min(frame_width, int(x_max))
        y_min = max(0, int(y_min))
        y_max = min(frame_height, int(y_max))

        return x_min, y_min, x_max, y_max

    def close(self):
        self.landmarker.close()
