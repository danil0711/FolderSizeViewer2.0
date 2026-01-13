from dataclasses import dataclass
from pathlib import Path


@dataclass
class ScanResult:
    path: Path
    size_bytes: int
    file_count: int
    error_count: int
