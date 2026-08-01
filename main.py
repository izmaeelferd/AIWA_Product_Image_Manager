import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow
from core.logger import setup_logger

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("AIWA Product Image Manager Pro")
    app.setOrganizationName("AIWA")

    # Set high DPI
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
