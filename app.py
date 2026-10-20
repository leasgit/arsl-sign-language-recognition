import os
import sys

import cv2
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from recognition import ArSLRecognizer


MODEL_PATH = "arsl_cnn_model.keras"
HAND_MODEL_PATH = "hand_landmarker.task"
CONFIDENCE_THRESHOLD = 0.40
RECOGNITION_INTERVAL_MS = 220

VARIANT_OPTIONS = {
    "aleff": ["ا", "أ", "إ", "آ"],
    "waw": ["و", "ؤ"],
    "ya": ["ي", "ئ"],
}

TRANSLATIONS = {
    "en": {
        "window_title": "ArSL Sign Recognition",
        "title": "Arabic Sign Language Recognition",
        "subtitle": "Show an Arabic Sign Language letter to the camera",
        "camera_placeholder": "Camera preview will appear here",
        "camera_error": "Could not open the camera. Please check camera permissions.",
        "detected_sign": "Detected sign",
        "waiting_camera": "Waiting for camera",
        "loading_model": "Loading recognition model...",
        "no_hand": "No hand detected",
        "uncertain": "Hold the sign steady",
        "model_error": "Recognition files are missing or could not be loaded.",
        "written_form": "Choose written form",
        "current_word": "Current word",
        "add_letter": "Add Letter",
        "delete": "Delete",
        "clear": "Clear",
        "privacy_note": "Camera processing stays on this computer.",
        "language_button": "العربية",
    },
    "ar": {
        "window_title": "التعرّف على لغة الإشارة العربية",
        "title": "التعرّف على حروف لغة الإشارة العربية",
        "subtitle": "اعرض حرفًا من لغة الإشارة العربية أمام الكاميرا",
        "camera_placeholder": "ستظهر معاينة الكاميرا هنا",
        "camera_error": "تعذّر فتح الكاميرا. يرجى التحقق من أذونات الكاميرا.",
        "detected_sign": "الحرف المكتشف",
        "waiting_camera": "بانتظار الكاميرا",
        "loading_model": "جارٍ تحميل نموذج التعرّف...",
        "no_hand": "لم يتم اكتشاف يد",
        "uncertain": "ثبّت الإشارة للحظة",
        "model_error": "ملفات التعرّف غير موجودة أو تعذّر تحميلها.",
        "written_form": "اختر الشكل الكتابي",
        "current_word": "الكلمة الحالية",
        "add_letter": "إضافة الحرف",
        "delete": "حذف",
        "clear": "مسح",
        "privacy_note": "تتم معالجة الكاميرا محليًا على هذا الجهاز.",
        "language_button": "English",
    },
}


class ArSLApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.resize(1100, 700)
        self.setMinimumSize(900, 600)

        self.current_language = "en"
        self.current_letter = ""
        self.current_class_name = None
        self.current_variant_group = None
        self.word_tokens = []
        self.camera_active = False
        self.camera_failed = False
        self.recognizer = None
        self.recognition_error = False
        self.latest_frame = None
        self.latest_bbox = None
        self.last_confidence = None
        self.status_key = "waiting_camera"

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(32, 22, 32, 28)
        main_layout.setSpacing(18)

        language_row = QHBoxLayout()
        language_row.addStretch()
        self.language_button = QPushButton()
        self.language_button.setObjectName("languageButton")
        self.language_button.setFixedWidth(100)
        self.language_button.clicked.connect(self.toggle_language)
        language_row.addWidget(self.language_button)
        main_layout.addLayout(language_row)

        self.title_label = QLabel()
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setObjectName("title")
        main_layout.addWidget(self.title_label)

        self.subtitle_label = QLabel()
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setObjectName("subtitle")
        main_layout.addWidget(self.subtitle_label)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(24)
        main_layout.addLayout(content_layout, 1)

        self.camera_label = QLabel()
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setMinimumSize(600, 430)
        self.camera_label.setObjectName("camera")
        content_layout.addWidget(self.camera_label, 3)

        panel = QWidget()
        panel.setObjectName("panel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(26, 26, 26, 26)
        panel_layout.setSpacing(16)
        content_layout.addWidget(panel, 2)

        self.detected_heading = QLabel()
        self.detected_heading.setAlignment(Qt.AlignCenter)
        self.detected_heading.setObjectName("sectionHeading")
        panel_layout.addWidget(self.detected_heading)

        self.letter_label = QLabel("—")
        self.letter_label.setAlignment(Qt.AlignCenter)
        self.letter_label.setLayoutDirection(Qt.RightToLeft)
        self.letter_label.setObjectName("letter")
        panel_layout.addWidget(self.letter_label)

        self.confidence_label = QLabel()
        self.confidence_label.setAlignment(Qt.AlignCenter)
        self.confidence_label.setObjectName("confidence")
        panel_layout.addWidget(self.confidence_label)

        self.variant_widget = QWidget()
        variant_layout = QVBoxLayout(self.variant_widget)
        variant_layout.setContentsMargins(0, 0, 0, 0)
        variant_layout.setSpacing(8)

        self.variant_heading = QLabel()
        self.variant_heading.setAlignment(Qt.AlignCenter)
        self.variant_heading.setObjectName("variantHeading")
        variant_layout.addWidget(self.variant_heading)

        variant_buttons_layout = QHBoxLayout()
        variant_buttons_layout.setSpacing(8)
        self.variant_buttons = []
        for index in range(4):
            button = QPushButton()
            button.setObjectName("variantButton")
            button.setCheckable(True)
            button.clicked.connect(lambda checked=False, i=index: self.select_variant(i))
            self.variant_buttons.append(button)
            variant_buttons_layout.addWidget(button)
        variant_layout.addLayout(variant_buttons_layout)

        self.variant_widget.setVisible(False)
        panel_layout.addWidget(self.variant_widget)

        panel_layout.addSpacing(10)

        self.word_heading = QLabel()
        self.word_heading.setAlignment(Qt.AlignCenter)
        self.word_heading.setObjectName("sectionHeading")
        panel_layout.addWidget(self.word_heading)

        self.word_label = QLabel("—")
        self.word_label.setAlignment(Qt.AlignCenter)
        self.word_label.setLayoutDirection(Qt.RightToLeft)
        self.word_label.setObjectName("word")
        panel_layout.addWidget(self.word_label)

        panel_layout.addStretch()

        self.add_button = QPushButton()
        self.delete_button = QPushButton()
        self.clear_button = QPushButton()

        self.add_button.clicked.connect(self.add_letter)
        self.delete_button.clicked.connect(self.delete_letter)
        self.clear_button.clicked.connect(self.clear_word)

        panel_layout.addWidget(self.add_button)

        secondary_buttons = QHBoxLayout()
        secondary_buttons.addWidget(self.delete_button)
        secondary_buttons.addWidget(self.clear_button)
        panel_layout.addLayout(secondary_buttons)

        self.note_label = QLabel()
        self.note_label.setWordWrap(True)
        self.note_label.setAlignment(Qt.AlignCenter)
        self.note_label.setObjectName("note")
        panel_layout.addWidget(self.note_label)

        self.setStyleSheet(
            """
            QMainWindow { background: #f4f6f8; }
            QLabel#title { font-size: 30px; font-weight: 700; color: #20252b; }
            QLabel#subtitle { font-size: 15px; color: #66707a; }
            QLabel#camera { background: #1e2329; color: #c8ced5; border-radius: 16px; font-size: 17px; }
            QWidget#panel { background: white; border-radius: 16px; }
            QLabel#sectionHeading { font-size: 16px; font-weight: 600; color: #4d5660; }
            QLabel#letter { font-size: 88px; font-weight: 700; color: #20252b; min-height: 120px; }
            QLabel#confidence { font-size: 14px; color: #68737d; }
            QLabel#variantHeading { font-size: 12px; color: #7a848e; }
            QLabel#word { font-size: 40px; font-weight: 600; color: #20252b; background: #f4f6f8; border-radius: 10px; padding: 14px; min-height: 62px; }
            QPushButton { min-height: 46px; border-radius: 9px; border: 1px solid #cbd2d9; background: white; color: #20252b; font-size: 15px; font-weight: 600; padding: 0 16px; }
            QPushButton:hover { background: #eef1f4; }
            QPushButton#primary { background: #20252b; color: white; border: none; }
            QPushButton#languageButton { min-height: 34px; max-height: 34px; font-size: 13px; padding: 0 12px; }
            QPushButton#variantButton { min-height: 38px; max-height: 38px; font-size: 20px; padding: 0 10px; }
            QPushButton#variantButton:checked { background: #20252b; color: white; border: none; }
            QLabel#note { font-size: 12px; color: #7a848e; }
            """
        )
        self.add_button.setObjectName("primary")
        self.add_button.setEnabled(False)

        self.apply_language()
        self.load_recognizer()
        self.start_camera()

    def load_recognizer(self):
        self.status_key = "loading_model"
        self.apply_language()

        if not os.path.isfile(MODEL_PATH) or not os.path.isfile(HAND_MODEL_PATH):
            self.recognition_error = True
            self.status_key = "model_error"
            self.apply_language()
            return

        try:
            self.recognizer = ArSLRecognizer(MODEL_PATH, HAND_MODEL_PATH)
        except Exception:
            self.recognition_error = True
            self.status_key = "model_error"
        else:
            self.status_key = "no_hand"
        self.apply_language()

    def start_camera(self):
        self.capture = cv2.VideoCapture(0)
        if not self.capture.isOpened():
            self.camera_failed = True
            self.camera_active = False
            self.apply_language()
            return

        self.camera_active = True
        self.camera_failed = False

        self.camera_timer = QTimer(self)
        self.camera_timer.timeout.connect(self.update_camera_frame)
        self.camera_timer.start(30)

        if self.recognizer is not None:
            self.recognition_timer = QTimer(self)
            self.recognition_timer.timeout.connect(self.run_recognition)
            self.recognition_timer.start(RECOGNITION_INTERVAL_MS)

        self.apply_language()

    def update_camera_frame(self):
        if not self.camera_active:
            return

        ok, frame = self.capture.read()
        if not ok:
            return

        self.latest_frame = frame.copy()
        display_frame = cv2.flip(frame, 1)

        if self.latest_bbox is not None:
            x1, y1, x2, y2 = self.latest_bbox
            frame_width = frame.shape[1]
            display_x1 = frame_width - x2
            display_x2 = frame_width - x1
            cv2.rectangle(display_frame, (display_x1, y1), (display_x2, y2), (90, 220, 120), 3)

        rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
        height, width, channels = rgb_frame.shape
        bytes_per_line = channels * width
        image = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format_RGB888).copy()
        pixmap = QPixmap.fromImage(image).scaled(
            self.camera_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.camera_label.setPixmap(pixmap)

    def run_recognition(self):
        if self.recognizer is None or self.latest_frame is None:
            return

        prediction = self.recognizer.predict(self.latest_frame)

        if prediction is None:
            self.current_letter = ""
            self.current_class_name = None
            self.latest_bbox = None
            self.last_confidence = None
            self.letter_label.setText("—")
            self.status_key = "no_hand"
            self.add_button.setEnabled(False)
            self.variant_widget.setVisible(False)
            self.update_status_display()
            return

        self.latest_bbox = prediction.bbox
        self.last_confidence = prediction.confidence

        if prediction.confidence < CONFIDENCE_THRESHOLD:
            self.current_letter = ""
            self.current_class_name = prediction.class_name
            self.letter_label.setText("—")
            self.status_key = "uncertain"
            self.add_button.setEnabled(False)
            self.variant_widget.setVisible(False)
        else:
            self.current_class_name = prediction.class_name
            self.status_key = None
            self.configure_written_form(prediction.class_name, prediction.arabic)
            self.add_button.setEnabled(True)

        self.update_status_display()

    def variant_group_for_class(self, class_name):
        if class_name in ("ya", "yaa"):
            return "ya"
        if class_name in VARIANT_OPTIONS:
            return class_name
        return None

    def configure_written_form(self, class_name, default_letter):
        group = self.variant_group_for_class(class_name)

        if group is None:
            self.current_variant_group = None
            self.current_letter = default_letter
            self.letter_label.setText(default_letter)
            self.variant_widget.setVisible(False)
            return

        options = VARIANT_OPTIONS[group]
        group_changed = group != self.current_variant_group
        self.current_variant_group = group
        self.variant_widget.setVisible(True)

        for index, button in enumerate(self.variant_buttons):
            if index < len(options):
                button.setText(options[index])
                button.setVisible(True)
                button.setEnabled(True)
            else:
                button.setVisible(False)
                button.setEnabled(False)
                button.setChecked(False)

        if group_changed or self.current_letter not in options:
            self.current_letter = options[0]

        for index, option in enumerate(options):
            self.variant_buttons[index].setChecked(option == self.current_letter)

        self.letter_label.setText(self.current_letter)

    def select_variant(self, index):
        if self.current_variant_group is None:
            return

        options = VARIANT_OPTIONS[self.current_variant_group]
        if index >= len(options):
            return

        self.current_letter = options[index]
        for button_index, button in enumerate(self.variant_buttons):
            button.setChecked(button_index == index)
        self.letter_label.setText(self.current_letter)

    def update_status_display(self):
        text = TRANSLATIONS[self.current_language]
        if self.last_confidence is not None:
            if self.status_key == "uncertain":
                self.confidence_label.setText(f"{text['uncertain']} · {self.last_confidence:.0%}")
            elif self.current_letter:
                self.confidence_label.setText(f"{self.last_confidence:.0%}")
            else:
                self.confidence_label.setText(text["no_hand"])
        elif self.status_key:
            self.confidence_label.setText(text[self.status_key])
        else:
            self.confidence_label.setText(text["waiting_camera"])

    def toggle_language(self):
        self.current_language = "ar" if self.current_language == "en" else "en"
        self.apply_language()

    def apply_language(self):
        text = TRANSLATIONS[self.current_language]

        self.setWindowTitle(text["window_title"])
        self.title_label.setText(text["title"])
        self.subtitle_label.setText(text["subtitle"])

        if self.camera_failed:
            self.camera_label.setText(text["camera_error"])
        elif not self.camera_active:
            self.camera_label.setText(text["camera_placeholder"])

        self.detected_heading.setText(text["detected_sign"])
        self.variant_heading.setText(text["written_form"])
        self.word_heading.setText(text["current_word"])
        self.add_button.setText(text["add_letter"])
        self.delete_button.setText(text["delete"])
        self.clear_button.setText(text["clear"])
        self.note_label.setText(text["privacy_note"])
        self.language_button.setText(text["language_button"])

        direction = Qt.RightToLeft if self.current_language == "ar" else Qt.LeftToRight
        self.centralWidget().setLayoutDirection(direction)
        self.title_label.setLayoutDirection(direction)
        self.subtitle_label.setLayoutDirection(direction)
        self.detected_heading.setLayoutDirection(direction)
        self.confidence_label.setLayoutDirection(direction)
        self.variant_heading.setLayoutDirection(direction)
        self.word_heading.setLayoutDirection(direction)
        self.note_label.setLayoutDirection(direction)
        self.add_button.setLayoutDirection(direction)
        self.delete_button.setLayoutDirection(direction)
        self.clear_button.setLayoutDirection(direction)

        self.update_status_display()
        self.update_word_display()

    def add_letter(self):
        if not self.current_letter:
            return
        self.word_tokens.append(self.current_letter)
        self.update_word_display()

    def delete_letter(self):
        if self.word_tokens:
            self.word_tokens.pop()
        self.update_word_display()

    def clear_word(self):
        self.word_tokens.clear()
        self.update_word_display()

    def update_word_display(self):
        word = "".join(self.word_tokens)
        self.word_label.setText(word if word else "—")

    def closeEvent(self, event):
        if hasattr(self, "camera_timer"):
            self.camera_timer.stop()
        if hasattr(self, "recognition_timer"):
            self.recognition_timer.stop()
        if hasattr(self, "capture") and self.capture.isOpened():
            self.capture.release()
        if self.recognizer is not None:
            self.recognizer.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ArSLApp()
    window.show()
    sys.exit(app.exec())
