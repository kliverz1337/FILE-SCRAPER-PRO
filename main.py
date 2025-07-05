import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication

# Add project root to the Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from ui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())