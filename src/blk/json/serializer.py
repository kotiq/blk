from _ctypes import PyObj_FromPtr
import re
import json
from json.encoder import _make_iterencode, encode_basestring_ascii, encode_basestring
import typing as t
from blk.types import *

__all__ = ['serialize', 'JSON', 'JSON_MIN', 'JSON_2']


class FloatEncoder(json.JSONEncoder):
    def iterencode(self, o, _one_shot=False):
        markers = {} if self.check_circular else None
        _encoder = encode_basestring_ascii if self.ensure_ascii else encode_basestring
        encoder = _make_iterencode(
            markers, self.default, _encoder, self.indent, floatstr,
            self.key_separator, self.item_separator, self.sort_keys,
            self.skipkeys, False)
        return encoder(o, 0)


class NoIndentEncoder(FloatEncoder):
    # https://stackoverflow.com/questions/13249415/how-to-implement-custom-indentation-when-pretty-printing-with-the-json-module

    fmt = r'@@{}@@'
    regex = re.compile(fmt.format(r'(\d+)'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs = dict(kwargs)
        del self.kwargs['indent']

    def default(self, o):
        if isinstance(o, Var):
            value = o.value
            if isinstance(value, Vector):
                return self.fmt.format(id(o))
            return value
        return super().default(o)

    def iterencode(self, o, _one_shot=False):
        for s in super().iterencode(o):
            m = self.regex.search(s)
            if m:
                id_ = int(m.group(1))
                var_ = PyObj_FromPtr(id_)
                text = json.dumps(var_.value, cls=FloatEncoder, **self.kwargs)
                s = s.replace(f'"{self.fmt.format(id_)}"', text)
            yield s


class Mapper:
    @classmethod
    def _map_section(cls, section: Section) -> t.Union[t.Sequence, t.Mapping]:
        raise NotImplementedError

    @classmethod
    def _map_value(cls, value: Value):
        if isinstance(value, (Section, t.Mapping)):
            return cls._map_section(value)
        elif isinstance(value, Float12):
            return tuple(Var(Float3(value[i:i+3])) for i in range(0, 10, 3))
        elif isinstance(value, Color):
            return f"#{''.join(format(x, '02x') for x in value)}"
        elif isinstance(value, Vector):
            return Var(value)
        elif isinstance(value, Float):
            return round(value, 4)
        elif isinstance(value, Bool):
            return bool(value)
        else:
            return value

    @classmethod
    def map(cls, root):
        return cls._map_section(root)


class JSONMapper(Mapper):
    @classmethod
    def _map_section(cls, section: Section) -> t.Union[t.Sequence, t.Mapping]:
        items = section.items()
        if not items:
            return []
        else:
            m: t.Union[list, dict] = {}
            for n, vs in items:
                if len(vs) == 1:
                    v = vs[0]
                    if isinstance(m, list):
                        m.append({n: cls._map_value(v)})
                    else:
                        m[n] = cls._map_value(v)
                else:
                    if not isinstance(m, list):
                        m = [{n: v} for n, v in m.items()]
                    m.extend({n: cls._map_value(v)} for v in vs)
            return m


class JSON2Mapper(Mapper):
    @classmethod
    def _map_section(cls, section: Section) -> t.Union[t.Sequence, t.Mapping]:
        items = section.items()
        if not items:
            return []
        else:
            return {n: list(map(cls._map_value, vs)) for n, vs in items}


class JSONMinMapper(Mapper):
    pass


JSON = 0
JSON_MIN = 1
JSON_2 = 3


def serialize(root: Section, ostream, out_type: int, is_sorted=False):
    mapper = {
        JSON: JSONMapper,
        JSON_MIN: JSONMinMapper,
        JSON_2: JSON2Mapper,
    }[out_type]
    if root:
        json.dump(mapper.map(root), ostream, cls=NoIndentEncoder, ensure_ascii=False, indent=2, separators=(',', ': '),
                  sort_keys=is_sorted)
