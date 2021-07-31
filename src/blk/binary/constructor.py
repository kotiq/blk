from io import BytesIO
from functools import partial
import typing as t
import construct as ct
from construct import len_, this
from blk.types import *
from blk.binary import codes_map

__all__ = ['TaggedOffset', 'bfs', 'FileStruct', 'RawCString', 'Names',
           'serialize_fat', 'serialize_fat_s', 'compose_fat', 'compose_names', 'compose_slim', 'serialize_slim',
           'ConstructError', 'ComposeError', 'SerializeError']


class ConstructError(Exception):
    pass


class ComposeError(ConstructError):
    pass


class SerializeError(ConstructError):
    pass


UByte.con = ct.Byte
Int.con = ct.Int32sl
Long.con = ct.Int64sl
Float.con = ct.Float32l
Bool.con = ct.Int32ul

Color.con = ct.ExprSymmetricAdapter(
    UByte.con[4],
    lambda o, c: tuple(reversed(o[:-1])) + (o[-1], ),
)

for c in (Float12, Float4, Float3, Float2, Int3, Int2):
    c.con = c.type.con[c.size]

RawCString = ct.NullTerminated(ct.GreedyBytes)

Name.con = ct.ExprAdapter(
    RawCString,
    lambda obj, ctx: Name.of(obj),
    lambda obj, ctx: obj.encode()
)

Str.con = ct.ExprAdapter(
    RawCString,
    lambda obj, ctx: Str.of(obj),
    lambda obj, ctx: obj.encode()
)

Names = ct.FocusedSeq(
    'names',
    'names_count' / ct.Rebuild(ct.VarInt, ct.len_(ct.this.names)),
    'names' / ct.Prefixed(ct.VarInt, Name.con[ct.this.names_count])
)

TaggedOffset = ct.ByteSwapped(ct.Bitwise(ct.Sequence(ct.Bit, ct.BitsInteger(31))))

ParamInfo = ct.NamedTuple(
    'ParamInfo',
    'name_id type_id data',
    ct.Sequence(
        'name_id' / ct.Int24ul,
        'type_id' / ct.Byte,
        'data' / ct.Bytes(4)
    )
)

BlockInfo = ct.NamedTuple(
    'BlockInfo',
    'name_id params_count blocks_count block_offset',
    ct.Sequence(
        'name_id' / ct.ExprAdapter(
            ct.VarInt,
            lambda obj, ctx: obj - 1 if obj else None,
            lambda obj, ctx: 0 if obj is None else obj + 1
        ),
        'params_count' / ct.VarInt,
        'blocks_count' / ct.VarInt,
        'block_offset' / ct.IfThenElse(this.blocks_count > 0, ct.VarInt, ct.Computed(None))
    )
)


FileStruct = """Структура файла, за исключением таблицы имен имен""" * ct.Struct(
    'blocks_count' / ct.Rebuild(ct.VarInt, len_(this.blocks)),
    'params_count' / ct.Rebuild(ct.VarInt, len_(this.params)),
    'params_data' / ct.Prefixed(ct.VarInt, ct.GreedyBytes),
    'params' / ParamInfo[this.params_count],
    'blocks' / BlockInfo[this.blocks_count],
)

SlimFile = """"Файл с таблицей имен в другом файле""" * ct.FocusedSeq(
    'file',
    ct.Const(b'\x00'),
    'file' / FileStruct,
)


class FileAdapter(ct.Adapter):
    def __init__(self, subcon,
                 names_or_names_map: t.Union[t.Sequence[EncodedStr], t.Mapping[Name, int]]):
        super().__init__(subcon)
        self.params_data: BytesIO = ...

        self.names_or_names_map = names_or_names_map
        self.strings_in_names = isinstance(names_or_names_map, t.Mapping)

    def parse_params_data(self, con: ct.Construct, offset):
        self.params_data.seek(offset)
        return con.parse_stream(self.params_data)

    def build_params_data(self, con, value):
        offset = self.params_data.tell()
        con.build_stream(value, self.params_data)
        return offset

    def _decode(self, obj: ct.Container, context, path) -> Section:
        self.params_data = BytesIO(obj.params_data)
        names: t.Sequence[Name] = self.names_or_names_map
        params = []
        blocks = []
        param_offset = 0

        for name_id, type_id, data in obj.params:
            name = names[name_id]
            cls = codes_map[type_id]
            if cls is Str:
                tag, offset = TaggedOffset.parse(data)
                init = names[offset] if tag else self.parse_params_data(cls.con, offset)
                value = cls.of(init)
            elif cls in (Float12, Float4, Float3, Float2, Int3, Int2, Long):
                offset = ct.Int32ul.parse(data)
                init = self.parse_params_data(cls.con, offset)
                value = cls(init)
            elif cls in (Color, Int, Float):
                init = cls.con.parse(data)
                value = cls(init)
            elif cls is Bool:
                init = cls.con.parse(data)
                value = true if init else false
            params.append((name, value))

        for name_id, *_ in obj.blocks:
            name = None if name_id is None else names[name_id]
            value = Section()
            blocks.append((name, value))

        for (_, params_count, blocks_count, block_offset), (_, section) in zip(obj.blocks, blocks):
            start = param_offset
            end = start + params_count
            for name, value in params[start:end]:
                section.append(name, value)
            param_offset = end

            if blocks_count:
                start = block_offset
                end = start + blocks_count
                for name, value in blocks[start:end]:
                    section.append(name, value)

        return blocks[0][1]

    def _encode(self, obj: Section, context, path) -> ct.Container:
        self.params_data = BytesIO()
        params = []
        blocks = []
        block_offset_var = Var(0)

        if isinstance(self.names_or_names_map, t.Mapping):
            names_map = self.names_or_names_map
        else:
            names_map = {name: i for i, name in enumerate(self.names_or_names_map)}

        values_maps: ct.Mapping[type, dict[Parameter, int]] = {
            Str: {},
            Float12: {},
            Float4: {},
            Float3: {},
            Float2: {},
            Int3: {},
            Int2: {},
            Long: {}
        }
        """value -> offset"""
        root_item = (None, obj)

        if not self.strings_in_names:
            bfs(root_item, partial(self.on_build_strings,
                                   map_=values_maps[Str]))
            pos = self.params_data.tell()
            pad = -pos % 4
            self.params_data.write(b'\x00'*pad)

        bfs(root_item, partial(self.on_visit, names_map=names_map, values_maps=values_maps, params=params,
                               blocks=blocks, block_offset_var=block_offset_var))

        return {
            'params_data': self.params_data.getvalue(),
            'params': params,
            'blocks': blocks
        }

    def on_build_strings(self, item, map_):
        value = item[1]

        if isinstance(value, Str):
            if value not in map_:
                map_[value] = self.build_params_data(Str.con, value)

    def on_visit(self, item, names_map, values_maps, params, blocks, block_offset_var):
        name, value = item
        name_id = names_map.get(name)  # None для root

        if isinstance(value, Parameter):
            cls = value.__class__

            if cls is Str:
                if self.strings_in_names:
                    map_ = names_map
                    tag = 1
                else:
                    map_ = values_maps[cls]
                    tag = 0
                offset = map_[value]
                data = TaggedOffset.build([tag, offset])
            elif cls in (Float12, Float4, Float3, Float2, Int3, Int2, Long):
                map_ = values_maps[cls]
                if value not in map_:
                    map_[value] = self.build_params_data(cls.con, value)
                offset = map_[value]
                data = ct.Int32ul.build(offset)
            elif cls in (Color, Int, Float, Bool):
                data = cls.con.build(value)

            params.append((name_id, value.code, data))

        elif isinstance(value, Section):
            params_count, blocks_count = value.size()

            if not blocks_count:
                block_offset = None
            else:
                if name_id is None:  # root
                    block_offset_var.value = 1
                block_offset = block_offset_var.value
                block_offset_var.value += blocks_count
            blocks.append((name_id, params_count, blocks_count, block_offset))


def bfs(item, func):
    """Обход секции в ширину.

    item: (Name, Section), пара корневой секции (None, root)
    func: (Name, Value) -> None
    """

    queue = [item]

    while queue:
        it = queue.pop(0)
        func(it)
        value = it[1]
        if isinstance(value, Section):
            for it in value.sorted_pairs():
                queue.append(it)


def compose_fat(istream) -> Section:
    """Сборка секции из потока со встроенными именами."""

    try:
        names = Names.parse_stream(istream)
        return FileAdapter(FileStruct, names).parse_stream(istream)
    except (TypeError, ValueError, ct.ConstructError) as e:
        raise ComposeError(e)


def serialize_fat(section, ostream):
    """Дамп секции со встроенными именами в поток.
    Все строковые параметры находятся в своем блоке."""

    names_map = {name: None for name in section.names()}
    Names.build_stream(names_map.keys(), ostream)
    FileAdapter(FileStruct, list(names_map.keys())).build_stream(section, ostream)


def serialize_fat_s(section, ostream):
    """Дамп секции со встроенными именами в поток.
    Все строковые параметры находятся в блоке имен"""

    names_map = {}
    for name in section.names():
        if name not in names_map:
            names_map[name] = len(names_map)

    def on_visit(item):
        value = item[1]
        if isinstance(value, Str):
            if value not in names_map:
                names_map[value] = len(names_map)

    root_item = (None, section)
    bfs(root_item, on_visit)
    Names.build_stream(names_map.keys(), ostream)
    FileAdapter(FileStruct, names_map).build_stream(section, ostream)


def compose_slim(names: t.Sequence[Name], istream) -> Section:
    """Сборка секции из потока. Имена в списке"""

    try:
        return FileAdapter(SlimFile, names).parse_stream(istream)
    except (TypeError, ValueError, ct.ConstructError) as e:
        raise ComposeError(str(e))


def compose_names(istream) -> t.Sequence[Name]:
    """Сборка списка имен из потока."""

    try:
        return Names.parse_stream(istream)
    except (TypeError, ValueError, ct.ConstructError) as e:
        raise ComposeError(str(e))


def serialize_slim(section, names_map: t.MutableMapping[EncodedStr, int], ostream):
    """Сборка секции c именами из отображения в поток.
    Отображение имен может расширяться.
    Все строковые параметры находятся в блоке имен.
    """

    def on_visit(item):
        value = item[1]
        if isinstance(value, Str):
            if value not in names_map:
                names_map[value] = len(names_map)

    root_item = (None, section)
    bfs(root_item, on_visit)
    FileAdapter(SlimFile, names_map).build_stream(section, ostream)
