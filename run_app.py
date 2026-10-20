import os
import sys

from PySide6.QtWidgets import QApplication


def get_app_directory():
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


# Keep resource paths predictable both during development and after packaging.
os.chdir(get_app_directory())

from app import ArSLApp


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ArSLApp()
    window.show()
    sys.exit(app.exec())
