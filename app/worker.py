# app/worker.py
from pathlib import Path
from typing import List

from PySide6.QtCore import QObject, Signal, Slot

from app.scanner import scan_folder
from app.models import ScanResult


class ScanWorker(QObject):
    """
    Worker, который:
    - сканирует все подпапки выбранной директории
    - сообщает прогресс в процентах
    - возвращает список ScanResult
    """

    progress = Signal(int)                  # 0..100
    finished = Signal(list)                 # list[ScanResult]
    error = Signal(str)

    def __init__(self, root_path: Path) -> None:
        super().__init__()
        self.root_path = root_path
        self._is_cancelled = False

    @Slot()
    def run(self) -> None:
        try:
            subfolders = self._get_subfolders(self.root_path)
            total = len(subfolders)

            results: List[ScanResult] = []

            if total == 0:
                self.progress.emit(100)
                self.finished.emit(results)
                return

            for index, folder in enumerate(subfolders, start=1):
                if self._is_cancelled:
                    return

                result = scan_folder(folder)
                results.append(result)

                percent = int(index / total * 100)
                self.progress.emit(percent)

            self.finished.emit(results)

        except Exception as e:
            self.error.emit(str(e))

    def cancel(self) -> None:
        self._is_cancelled = True

    def _get_subfolders(self, root: Path) -> List[Path]:
        try:
            return [p for p in root.iterdir() if p.is_dir()]
        except Exception:
            return []
