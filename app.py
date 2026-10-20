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


TRANSLATIONS = {
    "en": {
        "window_title": "ArSL Sign Recognition",
        "title": "Arabic Sign Language Recognition",
        "subtitle": "Show an Arabic Sign Language letter to the camera",
        "camera_placeholder": "Camera preview will appear here",
        "camera_error": "Could not open the camera. Please check camera permissions.",
        "detected_sign": "Detected sign",
        "waiting_camera": "Waiting for camera",
        "camera_ready": "Camera ready — recognition coming next",
        "current_word": "Current word",
        "add_letter": "Add Letter",
        "delete": "Delete",
        "clear": "Clear",
        "privacy_note": "Camera processing will stay on this computer.",
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
        "camera_ready": "الكاميرا جاهزة — سيتم ربط التعرّف في الخطوة التالية",
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
        self.word = ""
        self.camera_active = False
        self.camera_failed = False

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(32, 22, 32, 28)
        main_layout.setSpacing(18)

        # Language switcher
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

        # Live camera preview
        self.camera_label = QLabel()
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setMinimumSize(600, 430)
        self.camera_label.setObjectName("camera")
        content_layout.addWidget(self.camera_label, 3)

        # Recognition panel
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

        panel_layout.addSpacing(18)

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
            QMainWindow {
                background: #f4f6f8;
            }
            QLabel#title {
                font-size: 30px;
                font-weight: 700;
                color: #20252b;
            }
            QLabel#subtitle {
                font-size: 15px;
                color: #66707a;
            }
            QLabel#camera {
                background: #1e2329;
                color: #c8ced5;
                border-radius: 16px;
                font-size: 17px;
            }
            QWidget#panel {
                background: white;
                border-radius: 16px;
            }
            QLabel#sectionHeading {
                font-size: 16px;
                font-weight: 600;
                color: #4d5660;
            }
            QLabel#letter {
                font-size: 88px;
                font-weight: 700;
                color: #20252b;
                min-height: 120px;
            }
            QLabel#confidence {
                font-size: 14px;
                color: #68737d;
            }
            QLabel#word {
                font-size: 40px;
                font-weight: 600;
                color: #20252b;
                background: #f4f6f8;
                border-radius: 10px;
                padding: 14px;
                min-height: 62px;
            }
            QPushButton {
                min-height: 46px;
                border-radius: 9px;
                border: 1px solid #cbd2d9;
                background: white;
                color: #20252b;
                font-size: 15px;
                font-weight: 600;
                padding: 0 16px;
            }
            QPushButton:hover {
                background: #eef1f4;
            }
            QPushButton#primary {
                background: #20252b;
                color: white;
                border: none;
            }
            QPushButton#languageButton {
                min-height: 34px;
                max-height: 34px;
                font-size: 13px;
                padding: 0 12px;
            }
            QLabel#note {
                font-size: 12px;
                color: #7a848e;
            }
            """
        )
        self.add_button.setObjectName("primary")

        self.apply_language()
        self.start_camera()

    def start_camera(self):
        self.capture = cv2.VideoCapture(0)
        if not self.capture.isOpened():
            self.camera_failed = True
            self.camera_active = False
            self.apply_language()
            return

        self.camera_active = True
        self.camera_failed = False
        self.apply_language()

        self.camera_timer = QTimer(self)
        self.camera_timer.timeout.connect(self.update_camera_frame)
        self.camera_timer.start(30)

    def update_camera_frame(self):
        if not self.camera_active:
            return

        ok, frame = self.capture.read()
        if not ok:
            return

        # Mirror only the displayed preview so it feels natural to the user.
        # Recognition will later use the original unmirrored frame.
        display_frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)

        height, width, channels = rgb_frame.shape
        bytes_per_line = channels * width
        image = QImage(
            rgb_frame.data,
            width,
            height,
            bytes_per_line,
            QImage.Format_RGB888,
        ).copy()

        pixmap = QPixmap.fromImage(image)
        pixmap = pixmap.scaled(
            self.camera_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.camera_label.setPixmap(pixmap)

    def toggle_language(self):
        self.current_language = "ar" if self.current_language == "en" else "en"
        self.apply_language()

    def apply_language(self):
        text = TRANSLATIONS[self.current_language]

        self.setWindowTitle(text["window_title"])
        self.title_label.setText(text["title"])
        self.subtitle_label.setText(text["subtitle"])

        # Do not call setText while a live pixmap is being displayed, because
        # QLabel.setText() would clear the camera image.
        if self.camera_failed:
            self.camera_label.setText(text["camera_error"])
        elif not self.camera_active:
            self.camera_label.setText(text["camera_placeholder"])

        self.detected_heading.setText(text["detected_sign"])
        if self.camera_active:
            self.confidence_label.setText(text["camera_ready"])
        else:
            self.confidence_label.setText(text["waiting_camera"])
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
        self.word_heading.setLayoutDirection(direction)
        self.note_label.setLayoutDirection(direction)
        self.add_button.setLayoutDirection(direction)
        self.delete_button.setLayoutDirection(direction)
        self.clear_button.setLayoutDirection(direction)

        self.update_word_display()

    def add_letter(self):
        if not self.current_letter:
            return
        self.word += self.current_letter
        self.update_word_display()

    def delete_letter(self):
        if self.word:
            self.word = self.word[:-1]
        self.update_word_display()

    def clear_word(self):
        self.word = ""
        self.update_word_display()

    def update_word_display(self):
        self.word_label.setText(self.word if self.word else "—")

    def closeEvent(self, event):
        if hasattr(self, "camera_timer"):
            self.camera_timer.stop()
        if hasattr(self, "capture") and self.capture.isOpened():
            self.capture.release()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ArSLApp()
    window.show()
    sys.exit(app.exec())
