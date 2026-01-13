import sqlite3
import time
from pathlib import Path
from typing import Iterable

from app.core.logger import logger
from app.models import ScanResult


# версия логики сканирования
CACHE_VERSION = 1

# логический TTL кеша (например, 7 дней)
MAX_CACHE_AGE = 7 * 24 * 60 * 60


class ScanCache:
    def __init__(self, db_path: Path) -> None:
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        with self._conn:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS scan_cache (
                    path TEXT PRIMARY KEY,
                    size_bytes INTEGER NOT NULL,
                    file_count INTEGER NOT NULL,
                    error_count INTEGER NOT NULL,
                    scan_time REAL NOT NULL,
                    version INTEGER NOT NULL
                )
                """
            )

    # ------------------------------------------------------------------
    # ЧТЕНИЕ КЕША
    # ------------------------------------------------------------------

    def get_many(self, paths: Iterable[Path]) -> dict[Path, ScanResult]:
        """
        Возвращает только валидные кешированные результаты.
        Невалидные автоматически игнорируются.
        """
        
        logger.debug(f"Cache lookup for {len(paths)} paths")
        
        now = time.time()
        paths = list(paths)
        if not paths:
            return {}

        placeholders = ",".join("?" for _ in paths)
        
        try:
            
        
            rows = self._conn.execute(
                f"""
                SELECT path, size_bytes, file_count, error_count, scan_time
                FROM scan_cache
                WHERE path IN ({placeholders})
                AND version = ?
                """,
                [str(p) for p in paths] + [CACHE_VERSION],
            ).fetchall()
        except sqlite3.DatabaseError as de:
            logger.error(f"SQLite error during cache read: {de}")
            return {}

        valid: dict[Path, ScanResult] = {}

        for row in rows:
            path = Path(row["path"])
            scan_time = row["scan_time"]

            # 1. проверяем, что папка существует и доступна
            try:
                current_mtime = path.stat().st_mtime
            except OSError as oe:
                logger.warning(f"Cache skip (stat failed): {path} ({oe})")
                continue

            # 2. папка менялась после сканирования
            if current_mtime > scan_time:
                continue

            # 3. кеш слишком старый
            if now - scan_time > MAX_CACHE_AGE:
                continue

            valid[path] = ScanResult(
                path=path,
                size_bytes=row["size_bytes"],
                file_count=row["file_count"],
                error_count=row["error_count"],
            )

        return valid

    # ------------------------------------------------------------------
    # ЗАПИСЬ КЕША (BULK)
    # ------------------------------------------------------------------

    def save_many(self, results: Iterable[ScanResult]) -> None:
        """
        Bulk-сохранение результатов сканирования в одной транзакции.
        """
        now = time.time()
        
        logger.debug("Saving scan results to cache")

        rows = []
        for r in results:
            # если папка исчезла или нет доступа — не кешируем
            try:
                r.path.stat()
            except OSError as oe:
                logger.warning(f"Cache save skipped (stat failed): {r.path} ({oe})")
                continue

            rows.append(
                (
                    str(r.path),
                    r.size_bytes,
                    r.file_count,
                    r.error_count,
                    now,
                    CACHE_VERSION,
                )
            )

        if not rows:
            return
        
        try:
            

            with self._conn:
                self._conn.executemany(
                    """
                    INSERT OR REPLACE INTO scan_cache
                    (path, size_bytes, file_count, error_count, scan_time, version)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    rows,
                )
        except sqlite3.DatabaseError as de:
            logger.error(f"SQLite error during cache write: {de}")

    # ------------------------------------------------------------------
    # СЛУЖЕБНОЕ
    # ------------------------------------------------------------------

    def clear(self) -> None:
        """Полная очистка кеша"""
        with self._conn:
            self._conn.execute("DELETE FROM scan_cache")
