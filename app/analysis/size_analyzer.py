from pathlib import Path
from typing import Iterable
import numpy as np

from app.models import ScanResult


def detect_large_folders(
    results: Iterable[ScanResult],
    *,
    factor: float = 1.5,
    min_items: int = 5,
) -> set[Path]:
    """
    Определяет папки, которые аномально большие
    относительно остальных (IQR-модель).

    factor — коэффициент выброса (стандарт 1.5)
    min_items — минимальное количество папок для анализа
    """

    results = list(results)
    if len(results) < min_items:
        return set()

    sizes = np.array([r.size_bytes for r in results], dtype=np.float64)
    
    
    q1 = np.percentile(sizes, 25)
    q3 = np.percentile(sizes, 75)
    

    interquartile_range = q3 - q1
    if interquartile_range <= 0:
        return set()

    threshold = q3 + factor * interquartile_range

    return {r.path for r in results if r.size_bytes > threshold}
