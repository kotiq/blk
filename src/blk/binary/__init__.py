from ..types import *


codes_map = {
    0x00: Section,
    0x01: Str,
    0x02: Int,
    0x03: Float,
    0x04: Float2,
    0x05: Float3,
    0x06: Float4,
    0x07: Int2,
    0x08: Int3,
    0x09: Bool,
    0x0a: Color,
    0x0b: Float12,
    0x0c: Long,
}

for code, cls in codes_map.items():
    cls.code = code

from .constructor import (compose_fat, compose_slim, compose_names, serialize_fat, serialize_fat_s, serialize_slim,
                          ConstructError, ComposeError, SerializeError, serialize_names, bfs, update_names_map)

__all__ = ['compose_fat', 'compose_slim', 'compose_names', 'serialize_fat', 'serialize_fat_s', 'serialize_slim',
           'ConstructError', 'ComposeError', 'SerializeError', 'serialize_names', 'bfs', 'update_names_map']
