from loguru import logger
from pathlib import Path
import sys

LOG_DIR = Path.cwd()
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "folder_size_scanner.log"

logger.remove()

# Консоль (для dev)
logger.add(
    sys.stderr,
    level="INFO",
    format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}",
)

# Файл (всё подряд)
logger.add(
    LOG_FILE,
    level="DEBUG",
    rotation="5 MB",
    retention="14 days",
    compression="zip",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{line} | {message}",
)

__all__ = ["logger"]
