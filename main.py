# main.py
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from app.ui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)

    if len(sys.argv) < 2:
        print("Usage: folder_size_viewer <path>")
        sys.exit(1)

    root_path = Path(sys.argv[1])
    

    window = MainWindow(root_path)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
