# app/services/scan_service.py
from pathlib import Path
from typing import Callable, List

from app.models import ScanResult
from app.scanner import scan_folder
from app.cache import ScanCache


class ScanService:
    def __init__(self, cache: ScanCache) -> None:
        self.cache = cache

    def scan(
        self,
        root: Path,
        on_progress: Callable[[int], None],
        is_cancelled: Callable[[], bool],
    ) -> List[ScanResult]:

        subfolders = [p for p in root.iterdir() if p.is_dir()]
        total = len(subfolders)

        if total == 0:
            on_progress(100)
            return []

        cached = self.cache.get_many(subfolders)

        results: list[ScanResult] = []
        scanned: list[ScanResult] = []

        done = 0

        # 1. сразу добавляем кеш
        for path, result in cached.items():
            results.append(result)
            done += 1
            on_progress(int(done / total * 100))

        # 2. сканируем остальное
        for folder in subfolders:
            if folder in cached:
                continue

            if is_cancelled():
                break

            result = scan_folder(folder)
            results.append(result)
            scanned.append(result)

            done += 1
            on_progress(int(done / total * 100))

        # 3. сохраняем только реально отсканированное
        self.cache.save_many(scanned)

        return results
