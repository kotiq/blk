from enum import IntEnum

__all__ = [
    'Format',
    'dgen_float',
    'dgen_float_element',
]


class Format(IntEnum):
    """Выходной формат распаковщика."""

    RAW = -1
    JSON = 0
    STRICT_BLK = 2
    JSON_2 = 3
    JSON_3 = 4


def dgen_float(x: float) -> float:
    return round(x, 4)


def dgen_float_element(x: float) -> float:
    return float(format(x, 'e'))
