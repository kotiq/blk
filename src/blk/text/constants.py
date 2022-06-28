from blk.types import Bool, Color, Float, Float2, Float3, Float4, Float12, Int, Int2, Int3, Long, Str

__all__ = [
    'types_tags_map'
]

types_tags_map = {
    Bool: 'b',
    Str: 't',
    Int: 'i',
    Long: 'i64',
    Float: 'r',
    Int2: 'ip2',
    Int3: 'ip3',
    Color: 'c',
    Float2: 'p2',
    Float3: 'p3',
    Float4: 'p4',
    Float12: 'm',
}
