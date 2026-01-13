# app/ui/main_window.py
from pathlib import Path
from typing import List

from PySide6.QtWidgets import (
    QAbstractItemView,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QProgressBar,
    QLabel,
)
from PySide6.QtCore import QThread, Qt

from app.utils.size_format import format_bytes_grouped, format_size
from app.worker import ScanWorker
from app.models import ScanResult
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QStyle




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

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["", "Folder", "Size", "Files"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setColumnWidth(0, 32)


        
        
        
        
        self.table.cellClicked.connect(self._on_cell_clicked)
        
        # Отключаем редактирование
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
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
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        
        folder_icon = self.style().standardIcon(QStyle.SP_DirIcon)

        for result in results:
            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(result.path.name))
            
            icon_item = QTableWidgetItem()
            icon_item.setIcon(folder_icon)
            icon_item.setData(Qt.UserRole, str(result.path))
            icon_item.setFlags(Qt.ItemIsEnabled)

            self.table.setItem(row, 0, icon_item)
            
            folder_item = QTableWidgetItem(result.path.name)
            folder_item.setToolTip(str(result.path))

            self.table.setItem(row, 1, folder_item)
                        
            
            size_item = QTableWidgetItem(format_size(result.size_bytes))
            size_item.setToolTip(f"{format_bytes_grouped(result.size_bytes)} bytes")
            size_item.setData(Qt.UserRole, result.size_bytes)
            
            self.table.setItem(row, 2, size_item)
            
            
            self.table.setItem(row, 3, QTableWidgetItem(str(result.file_count)))
        self.table.setSortingEnabled(True)
        
    
    def _on_cell_clicked(self, row: int, column: int) -> None:
        # если клик не по первой колонке
        if column != 0:
            return

        item = self.table.item(row, 0)
        if not item:
            return

        path = item.data(Qt.UserRole)
        if not path:
            return

        QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        

