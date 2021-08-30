from io import BytesIO
from collections import OrderedDict
import typing as t
import construct as ct
from construct import len_, this
from blk.types import *
from .constants import *

__all__ = ['TaggedOffset', 'FileStruct', 'RawCString', 'Names', 'types_cons_map',
           'serialize_fat', 'serialize_fat_s', 'compose_fat', 'compose_names', 'compose_slim', 'serialize_slim',
           'ConstructError', 'ComposeError', 'SerializeError', 'update_names_map', 'serialize_names']


class ConstructError(Exception):
    pass


class ComposeError(ConstructError):
    pass


class SerializeError(ConstructError):
    pass


RawCString = ct.NullTerminated(ct.GreedyBytes).compile()

name_con = ct.ExprAdapter(
    RawCString,
    lambda obj, ctx: Name.of(obj),
    lambda obj, ctx: obj.encode()
).compile()

str_con = ct.ExprAdapter(
    RawCString,
    lambda obj, ctx: Str.of(obj),
    lambda obj, ctx: obj.encode()
).compile()

types_cons_map = {
    UByte: ct.Byte.compile(),
    Int: ct.Int32sl.compile(),
    Long: ct.Int64sl.compile(),
    Float: ct.Float32l.compile(),
    Bool: ct.Int32ul.compile(),
    Str: str_con,
    Name: name_con,
}

types_cons_map[Color] = ct.ExprSymmetricAdapter(
    (types_cons_map[Color.type])[Color.size],
    lambda o, _: tuple(reversed(o[:-1])) + (o[-1], ),
).compile()

for c in (Float12, Float4, Float3, Float2, Int3, Int2):
    types_cons_map[c] = (types_cons_map[c.type])[c.size].compile()

Names = ct.FocusedSeq(
    'names',
    'names_count' / ct.Rebuild(ct.VarInt, ct.len_(ct.this.names)),
    'names' / ct.Prefixed(ct.VarInt, (types_cons_map[Name])[ct.this.names_count])
).compile()

TaggedOffset = ct.ByteSwapped(ct.Bitwise(ct.Sequence(ct.Bit, ct.BitsInteger(31)))).compile()

ParamInfo = ct.NamedTuple(
    'ParamInfo',
    'name_id type_id data',
    ct.Sequence(
        'name_id' / ct.Int24ul,
        'type_id' / ct.Byte,
        'data' / ct.Bytes(4)
    )
).compile()

Id_of_root = None

BlockInfo = ct.NamedTuple(
    'BlockInfo',
    'name_id params_count blocks_count block_offset',
    ct.Sequence(
        'name_id' / ct.ExprAdapter(
            ct.VarInt,
            lambda obj, ctx: obj - 1 if obj else Id_of_root,
            lambda obj, ctx: 0 if obj is Name.of_root else obj + 1
        ),
        'params_count' / ct.VarInt,
        'blocks_count' / ct.VarInt,
        'block_offset' / ct.IfThenElse(this.blocks_count > 0, ct.VarInt, ct.Computed(None))
    )
).compile()


FileStruct = """Структура файла, за исключением таблицы имен имен""" * ct.Struct(
    'blocks_count' / ct.Rebuild(ct.VarInt, len_(this.blocks)),
    'params_count' / ct.Rebuild(ct.VarInt, len_(this.params)),
    'params_data' / ct.Prefixed(ct.VarInt, ct.GreedyBytes),
    'params' / ParamInfo[this.params_count],
    'blocks' / BlockInfo[this.blocks_count],
).compile()

SlimFile = """"Файл с таблицей имен в другом файле""" * ct.FocusedSeq(
    'file',
    ct.Const(b'\x00'),
    'file' / FileStruct,
).compile()

Pair = t.Tuple[Name, Value]
NamesI = t.Iterable[Name]
NamesT = t.Sequence[Name]
NamesMap = t.OrderedDict[t.Union[Name, Str], int]
LongValue = t.Union[Str, Float12, Float4, Float3, Float2, Int3, Int2, Long]
LongValueType = t.Union[t.Type[Str], t.Type[Float12], t.Type[Float4], t.Type[Float3], t.Type[Float2], t.Type[Int3],
                        t.Type[Int2], t.Type[Long]]
ParametersMap = t.OrderedDict[t.Union[Name, LongValue], int]
ValuesMap = t.Mapping[LongValueType, ParametersMap]
ParameterInfo = t.Tuple[int, int, bytes]
ParameterInfos = t.MutableSequence[ParameterInfo]
BlockInfoT = t.Tuple[int, int, int, t.Optional[int]]
BlockInfos = t.MutableSequence[BlockInfoT]
ParameterT = t.Tuple[Name, Parameter]
Parameters = t.MutableSequence[ParameterT]
SectionT = t.Tuple[t.Optional[Name], Section]
Sections = t.MutableSequence[SectionT]


def getvalue(val: t.Union[callable, t.Any], context) -> t.Any:
    return val(context) if callable(val) else val


class FileAdapter(ct.Adapter):
    def __init__(self, subcon, names_or_names_map: t.Union[t.Callable, NamesT, NamesI, NamesMap]):
        super().__init__(subcon)
        self.params_data: BytesIO = ...

        self.names_or_names_map = names_or_names_map
        self.strings_in_names: bool = ...

    def parse_params_data(self, con: ct.Construct, offset) -> t.Any:
        self.params_data.seek(offset)
        return con.parse_stream(self.params_data)

    def build_params_data(self, con: ct.Construct, value) -> int:
        offset = self.params_data.tell()
        con.build_stream(value, self.params_data)
        return offset

    def _decode(self, obj: ct.Container, context, path) -> Section:
        names_or_names_map: NamesT = getvalue(self.names_or_names_map, context)
        self.strings_in_names = isinstance(names_or_names_map, t.Mapping)

        self.params_data = BytesIO(obj.params_data)
        names = names_or_names_map
        params: Parameters = []
        blocks: Sections = []
        param_offset = 0

        for name_id, type_id, data in obj.params:
            name = names[name_id]
            cls = codes_types_map[type_id]
            con = types_cons_map[cls]
            if cls is Str:
                tag, offset = TaggedOffset.parse(data)
                init = names[offset] if tag else self.parse_params_data(con, offset)
                value = cls.of(init)
            elif cls in (Float12, Float4, Float3, Float2, Int3, Int2, Long):
                offset = ct.Int32ul.parse(data)
                init = self.parse_params_data(con, offset)
                value = cls(init)
            elif cls in (Color, Int, Float):
                init = con.parse(data)
                value = cls(init)
            elif cls is Bool:
                init = con.parse(data)
                value = true if init else false
            params.append((name, value))

        for name_id, *_ in obj.blocks:
            name = Name.of_root if name_id is Id_of_root else names[name_id]
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
        names_or_names_map: t.Union[NamesI, NamesMap] = getvalue(self.names_or_names_map, context)
        self.strings_in_names = isinstance(names_or_names_map, t.Mapping)

        self.params_data = BytesIO()
        params: ParameterInfos = []
        blocks: BlockInfos = []
        block_offset_var = Var(0)

        if isinstance(names_or_names_map, t.OrderedDict):
            names_map = names_or_names_map
        else:
            names_map = OrderedDict((name, i) for i, name in enumerate(names_or_names_map))

        values_maps: ValuesMap = dict((cls, OrderedDict())
                                      for cls in (Str, Float12, Float4, Float3, Float2, Int2, Int3, Long))
        """value -> offset"""

        if not self.strings_in_names:
            for item in obj.bfs_sorted_pairs():
                self.build_string(item, values_maps[Str])

            pos = self.params_data.tell()
            pad = -pos % 4
            self.params_data.write(b'\x00'*pad)

        for item in obj.bfs_sorted_pairs():
            self.build_item(item, names_map, values_maps, params, blocks, block_offset_var)

        return {
            'params_data': self.params_data.getvalue(),
            'params': params,
            'blocks': blocks
        }

    def build_string(self, item: Pair, map_: NamesMap):
        value = item[1]

        if isinstance(value, Str):
            if value not in map_:
                con = types_cons_map[Str]
                map_[value] = self.build_params_data(con, value)

    def build_item(self, item: Pair, names_map: NamesMap, values_maps: ValuesMap,
                   params: ParameterInfos, blocks: BlockInfos, block_offset_var: Var):
        name, value = item
        name_id = names_map.get(name, Name.of_root)

        if isinstance(value, Parameter):
            cls = value.__class__
            code = types_codes_map[cls]
            con = types_cons_map[cls]

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
                    map_[value] = self.build_params_data(con, value)
                offset = map_[value]
                data = ct.Int32ul.build(offset)
            elif cls in (Color, Int, Float, Bool):
                data = con.build(value)

            params.append((name_id, code, data))

        elif isinstance(value, Section):
            params_count, blocks_count = value.size()

            if not blocks_count:
                block_offset = None
            else:
                if name_id is Name.of_root:  # root
                    block_offset_var.value = 1
                block_offset = block_offset_var.value
                block_offset_var.value += blocks_count
            blocks.append((name_id, params_count, blocks_count, block_offset))


def compose_fat(istream) -> Section:
    """Сборка секции из потока со встроенными именами."""

    try:
        names = Names.parse_stream(istream)
        return FileAdapter(FileStruct, names).parse_stream(istream)
    except (TypeError, ValueError, ct.ConstructError) as e:
        raise ComposeError(e)


def serialize_fat(section: Section, ostream):
    """Дамп секции со встроенными именами в поток.
    Все строковые параметры находятся в своем блоке."""

    names_map = OrderedDict.fromkeys(section.names())
    try:
        names = names_map.keys()
        Names.build_stream(names, ostream)
        FileAdapter(FileStruct, names).build_stream(section, ostream)
    except (TypeError, ValueError, ct.ConstructError) as e:
        raise SerializeError(str(e))


def serialize_fat_s(section: Section, ostream):
    """Дамп секции со встроенными именами в поток.
    Все строковые параметры находятся в блоке имен"""

    names_map = OrderedDict()
    update_names_map(names_map, section)
    try:
        Names.build_stream(names_map.keys(), ostream)
        FileAdapter(FileStruct, names_map).build_stream(section, ostream)
    except (TypeError, ValueError, ct.ConstructError) as e:
        raise SerializeError(str(e))


def compose_slim(names: NamesT, istream) -> Section:
    """Сборка секции из потока. Имена в списке."""

    try:
        return FileAdapter(SlimFile, names).parse_stream(istream)
    except (TypeError, ValueError, ct.ConstructError) as e:
        raise ComposeError(str(e))


def compose_names(istream) -> NamesT:
    """Сборка списка имен из потока."""

    try:
        return Names.parse_stream(istream)
    except (TypeError, ValueError, ct.ConstructError) as e:
        raise ComposeError(str(e))


def serialize_slim(section, names_map: NamesMap, ostream):
    """Сборка секции c именами из отображения в поток.
    Отображение имен может расширяться.
    Все строковые параметры находятся в блоке имен.
    """

    add_new_strings(names_map, section)
    try:
        FileAdapter(SlimFile, names_map).build_stream(section, ostream)
    except (TypeError, ValueError, ct.ConstructError) as e:
        raise SerializeError(str(e))


def add_new_names(names_map: NamesMap, section: Section):
    for name in section.names():
        if name not in names_map:
            names_map[name] = len(names_map)


def add_new_strings(names_map: NamesMap, section: Section):
    for item in section.bfs_sorted_pairs():
        value = item[1]
        if isinstance(value, Str):
            if value not in names_map:
                names_map[value] = len(names_map)


def update_names_map(names_map: NamesMap, section: Section):
    add_new_names(names_map, section)
    add_new_strings(names_map, section)


def serialize_names(names: NamesT, ostream):
    """Сборка имен в поток."""

    try:
        Names.build_stream(names, ostream)
    except (TypeError, ValueError, ct.ConstructError) as e:
        raise SerializeError(str(e))
