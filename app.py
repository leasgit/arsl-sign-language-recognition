import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class ArSLApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ArSL Sign Recognition")
        self.resize(1100, 700)
        self.setMinimumSize(900, 600)

        self.current_letter = ""
        self.word = ""

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(32, 28, 32, 28)
        main_layout.setSpacing(22)

        title = QLabel("Arabic Sign Language Recognition")
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("title")
        main_layout.addWidget(title)

        subtitle = QLabel("Show an Arabic Sign Language letter to the camera")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setObjectName("subtitle")
        main_layout.addWidget(subtitle)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(24)
        main_layout.addLayout(content_layout, 1)

        # Camera area — the real webcam feed will be connected in the next step.
        self.camera_label = QLabel("Camera preview will appear here")
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

        detected_heading = QLabel("Detected sign")
        detected_heading.setAlignment(Qt.AlignCenter)
        detected_heading.setObjectName("sectionHeading")
        panel_layout.addWidget(detected_heading)

        self.letter_label = QLabel("—")
        self.letter_label.setAlignment(Qt.AlignCenter)
        self.letter_label.setLayoutDirection(Qt.RightToLeft)
        self.letter_label.setObjectName("letter")
        panel_layout.addWidget(self.letter_label)

        self.confidence_label = QLabel("Waiting for camera")
        self.confidence_label.setAlignment(Qt.AlignCenter)
        self.confidence_label.setObjectName("confidence")
        panel_layout.addWidget(self.confidence_label)

        panel_layout.addSpacing(18)

        word_heading = QLabel("Current word")
        word_heading.setAlignment(Qt.AlignCenter)
        word_heading.setObjectName("sectionHeading")
        panel_layout.addWidget(word_heading)

        self.word_label = QLabel("—")
        self.word_label.setAlignment(Qt.AlignCenter)
        self.word_label.setLayoutDirection(Qt.RightToLeft)
        self.word_label.setObjectName("word")
        panel_layout.addWidget(self.word_label)

        panel_layout.addStretch()

        self.add_button = QPushButton("Add Letter")
        self.delete_button = QPushButton("Delete")
        self.clear_button = QPushButton("Clear")

        self.add_button.clicked.connect(self.add_letter)
        self.delete_button.clicked.connect(self.delete_letter)
        self.clear_button.clicked.connect(self.clear_word)

        panel_layout.addWidget(self.add_button)

        secondary_buttons = QHBoxLayout()
        secondary_buttons.addWidget(self.delete_button)
        secondary_buttons.addWidget(self.clear_button)
        panel_layout.addLayout(secondary_buttons)

        note = QLabel("Camera processing will stay on this computer.")
        note.setWordWrap(True)
        note.setAlignment(Qt.AlignCenter)
        note.setObjectName("note")
        panel_layout.addWidget(note)

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
            QLabel#note {
                font-size: 12px;
                color: #7a848e;
            }
            """
        )
        self.add_button.setObjectName("primary")

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ArSLApp()
    window.show()
    sys.exit(app.exec())
