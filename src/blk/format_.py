from enum import IntEnum

__all__ = [
    'Format',
]


class Format(IntEnum):
    """Выходной формат распаковщика."""

    RAW = -1
    JSON = 0
    STRICT_BLK = 2
    JSON_2 = 3
    JSON_3 = 4
