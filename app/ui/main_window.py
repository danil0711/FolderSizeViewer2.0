# app/ui/main_window.py
from pathlib import Path
from typing import List

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QProgressBar,
    QLabel,
)
from PySide6.QtCore import QThread

from app.worker import ScanWorker
from app.models import ScanResult


class MainWindow(QMainWindow):
    def __init__(self, root_path: Path) -> None:
        super().__init__()

        self.setWindowTitle("Folder Size Viewer")
        self.resize(600, 400)

        self.root_path = root_path

        self._thread: QThread | None = None
        self._worker: ScanWorker | None = None

        self._build_ui()
        self._start_scan()

    def _build_ui(self) -> None:
        central = QWidget(self)
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)

        self.path_label = QLabel(str(self.root_path))
        layout.addWidget(self.path_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Folder", "Size (bytes)", "Files"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

    def _start_scan(self) -> None:
        self._thread = QThread(self)
        self._worker = ScanWorker(self.root_path)

        self._worker.moveToThread(self._thread)

        # сигналы
        self._thread.started.connect(self._worker.run)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)

        # корректное завершение
        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)

        self._thread.start()

    # ---------- slots ----------

    def _on_progress(self, percent: int) -> None:
        self.progress_bar.setValue(percent)

    def _on_finished(self, results: List[ScanResult]) -> None:
        self.progress_bar.setValue(100)
        self._populate_table(results)

    def _on_error(self, message: str) -> None:
        self.path_label.setText(f"Error: {message}")

    def _populate_table(self, results: List[ScanResult]) -> None:
        self.table.setRowCount(0)

        for result in results:
            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(result.path.name))
            self.table.setItem(row, 1, QTableWidgetItem(str(result.size_bytes)))
            self.table.setItem(row, 2, QTableWidgetItem(str(result.file_count)))
