def format_size(num_bytes: int) -> str:
    """
    Человекочитаемый формат размера.
    """
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if num_bytes < 1024:
            return f"{num_bytes:.2f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.2f} PB"


def format_bytes_grouped(num_bytes: int) -> str:
    """
    Точное значение с разделением по разрядам.
    """
    return f"{num_bytes:,}".replace(",", " ")