from blk.types import Bool, Color, Float, Float2, Float3, Float4, Float12, Int, Int2, Int3, Long, Section, Str

__all__ = [
    'codes_types_map',
    'types_codes_map'
]


types_codes_map = {
    Section: 0x00,
    Str: 0x01,
    Int: 0x02,
    Float: 0x03,
    Float2: 0x04,
    Float3: 0x05,
    Float4: 0x06,
    Int2: 0x07,
    Int3: 0x08,
    Bool: 0x09,
    Color: 0x0a,
    Float12: 0x0b,
    Long: 0x0c
}

codes_types_map = {v: k for k, v in types_codes_map.items()}
