# app/worker.py
from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from app.cache import ScanCache
from app.core.logger import logger
from app.scan_service import ScanService

CACHE_PATH = Path.cwd() / ".folder_size_cache.sqlite"


class ScanWorker(QObject):
    progress = Signal(int)
    finished = Signal(list)
    error = Signal(str)

    def __init__(self, root_path: Path, force_rescan: bool = False) -> None:
        super().__init__()
        self.root_path = root_path
        self._is_cancelled = False
        self.force_rescan = force_rescan

    @Slot()
    def run(self) -> None:
        try:
            cache = ScanCache(CACHE_PATH)
            service = ScanService(cache)

            results = service.scan(
                root=self.root_path,
                on_progress=self.progress.emit,
                is_cancelled=lambda: self._is_cancelled,
                force_rescan=self.force_rescan
            )

            self.finished.emit(results)

        except Exception as e:
            logger.error(f"Worker crashed: {e}")
            self.error.emit(str(e))
            
    def cancel(self):
        self._is_cancelled = True
        None
