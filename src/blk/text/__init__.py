from ..types import *


tags_map = {
    'b': Bool,
    't': Str,
    'i': Int,
    'i64': Long,
    'r': Float,
    'ip2': Int2,
    'ip3': Int3,
    'c': Color,
    'p2': Float2,
    'p3': Float3,
    'p4': Float4,
    'm': Float12,
}

for tag, cls in tags_map.items():
    cls.tag = tag


from .serializer import serialize, DefaultDialect, StrictDialect
__all__ = ['serialize', 'DefaultDialect', 'StrictDialect']
