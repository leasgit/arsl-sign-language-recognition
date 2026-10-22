import os
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QSplashScreen


def get_app_directory():
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def create_splash():
    width, height = 520, 240
    pixmap = QPixmap(width, height)
    pixmap.fill(QColor("#f4f6f8"))

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    painter.setPen(QColor("#20252b"))
    title_font = QFont("Segoe UI", 20)
    title_font.setBold(True)
    painter.setFont(title_font)
    painter.drawText(
        30,
        55,
        width - 60,
        70,
        Qt.AlignCenter,
        "Arabic Sign Language Recognition",
    )

    painter.setPen(QColor("#66707a"))
    loading_font = QFont("Segoe UI", 12)
    painter.setFont(loading_font)
    painter.drawText(
        30,
        135,
        width - 60,
        55,
        Qt.AlignCenter,
        "Loading...   •   جارٍ التحميل...",
    )

    painter.end()

    splash = QSplashScreen(pixmap)
    splash.setWindowFlag(Qt.WindowStaysOnTopHint, True)
    return splash


# Keep resource paths predictable both during development and after packaging.
os.chdir(get_app_directory())


if __name__ == "__main__":
    app = QApplication(sys.argv)

    icon_path = os.path.join("assets", "app_icon.ico")
    if os.path.isfile(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    splash = create_splash()
    splash.show()
    app.processEvents()

    # Import the heavier recognition application only after the splash is visible.
    from app import ArSLApp

    splash.showMessage(
        "Loading recognition model...",
        Qt.AlignBottom | Qt.AlignHCenter,
        QColor("#66707a"),
    )
    app.processEvents()

    window = ArSLApp()
    if os.path.isfile(icon_path):
        window.setWindowIcon(QIcon(icon_path))
    window.show()
    splash.finish(window)

    sys.exit(app.exec())
