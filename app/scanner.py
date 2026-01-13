from pathlib import Path
import os
from app.models import ScanResult

FILE_ATTRIBUTE_REPARSE_POINT = 0x400

def _is_safe_dir(entry: os.DirEntry) -> bool:
    """
    Безопасно ли входить в каталог:
    - не symlink
    - не junction / reparse point
    """
    try:
        if entry.is_symlink():
            return False

        stat = entry.stat(follow_symlinks=False)
        if hasattr(stat, "st_file_attributes"):
            if stat.st_file_attributes & FILE_ATTRIBUTE_REPARSE_POINT:
                return False

        return True

    except OSError:
        return False


def scan_folder(path: Path) -> ScanResult:
    total_size = 0
    total_files = 0
    errors = 0

    stack: list[Path] = [path]

    while stack:
        current = stack.pop()

        try:
            with os.scandir(current) as it:
                for entry in it:
                    try:
                        if entry.is_file(follow_symlinks=False):
                            stat = entry.stat(follow_symlinks=False)
                            total_size += stat.st_size
                            total_files += 1

                        elif entry.is_dir(follow_symlinks=False):
                            if _is_safe_dir(entry):
                                stack.append(Path(entry.path))

                    except (PermissionError, FileNotFoundError):
                        errors += 1

        except (PermissionError, FileNotFoundError):
            errors += 1

    return ScanResult(
        path=path,
        size_bytes=total_size,
        file_count=total_files,
        error_count=errors,
    )