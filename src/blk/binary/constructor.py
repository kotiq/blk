from io import BytesIO
from collections import OrderedDict
import typing as t
import construct as ct
from construct import len_, this
from blk.types import *
from blk.binary import codes_map

__all__ = ['TaggedOffset', 'FileStruct', 'RawCString', 'Names',
           'serialize_fat', 'serialize_fat_s', 'compose_fat', 'compose_names', 'compose_slim', 'serialize_slim',
           'ConstructError', 'ComposeError', 'SerializeError', 'update_names_map', 'serialize_names']


class ConstructError(Exception):
    pass


class ComposeError(ConstructError):
    pass


class SerializeError(ConstructError):
    pass


UByte.con = ct.Byte.compile()
Int.con = ct.Int32sl.compile()
Long.con = ct.Int64sl.compile()
Float.con = ct.Float32l.compile()
Bool.con = ct.Int32ul.compile()

Color.con = ct.ExprSymmetricAdapter(
    UByte.con[4],
    lambda o, c: tuple(reversed(o[:-1])) + (o[-1], ),
).compile()

for c in (Float12, Float4, Float3, Float2, Int3, Int2):
    c.con = c.type.con[c.size].compile()

RawCString = ct.NullTerminated(ct.GreedyBytes).compile()

Name.con = ct.ExprAdapter(
    RawCString,
    lambda obj, ctx: Name.of(obj),
    lambda obj, ctx: obj.encode()
).compile()

Str.con = ct.ExprAdapter(
    RawCString,
    lambda obj, ctx: Str.of(obj),
    lambda obj, ctx: obj.encode()
).compile()

Names = ct.FocusedSeq(
    'names',
    'names_count' / ct.Rebuild(ct.VarInt, ct.len_(ct.this.names)),
    'names' / ct.Prefixed(ct.VarInt, Name.con[ct.this.names_count])
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

ItemT = t.Tuple[Name, Value]
NamesIT = t.Iterable[Name]
NamesT = t.Sequence[Name]
NamesMapT = t.OrderedDict[t.Union[Name, Str], int]
LongValueT = t.Union[Str, Float12, Float4, Float3, Float2, Int3, Int2, Long]
ParametersMapT = t.OrderedDict[t.Union[Name, LongValueT], int]
ValuesMapT = t.Mapping[type, ParametersMapT]
ParameterInfoT = t.Tuple[int, int, bytes]
ParameterInfosT = t.MutableSequence[ParameterInfoT]
BlockInfoT = t.Tuple[int, int, int, t.Optional[int]]
BlockInfosT = t.MutableSequence[BlockInfoT]
ParameterT = t.Tuple[Name, Parameter]
ParametersT = t.MutableSequence[ParameterT]
SectionT = t.Tuple[t.Optional[Name], Section]
SectionsT = t.MutableSequence[SectionT]


def getvalue(val: t.Union[callable, t.Any], context) -> t.Any:
    return val(context) if callable(val) else val


class FileAdapter(ct.Adapter):
    def __init__(self, subcon, names_or_names_map: t.Union[t.Callable, NamesT, NamesIT, NamesMapT]):
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
        params: ParametersT = []
        blocks: SectionsT = []
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
        names_or_names_map: t.Union[NamesIT, NamesMapT] = getvalue(self.names_or_names_map, context)
        self.strings_in_names = isinstance(names_or_names_map, t.Mapping)

        self.params_data = BytesIO()
        params: ParameterInfosT = []
        blocks: BlockInfosT = []
        block_offset_var = Var(0)

        if isinstance(names_or_names_map, t.OrderedDict):
            names_map = names_or_names_map
        else:
            names_map = OrderedDict((name, i) for i, name in enumerate(names_or_names_map))

        values_maps: ValuesMapT = dict((cls, OrderedDict())
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

    def build_string(self, item: ItemT, map_: NamesMapT):
        value = item[1]

        if isinstance(value, Str):
            if value not in map_:
                map_[value] = self.build_params_data(Str.con, value)

    def build_item(self, item: ItemT, names_map: NamesMapT, values_maps: ValuesMapT,
                   params: ParameterInfosT, blocks: BlockInfosT, block_offset_var: Var):
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


def serialize_slim(section, names_map: NamesMapT, ostream):
    """Сборка секции c именами из отображения в поток.
    Отображение имен может расширяться.
    Все строковые параметры находятся в блоке имен.
    """

    add_new_strings(names_map, section)
    try:
        FileAdapter(SlimFile, names_map).build_stream(section, ostream)
    except (TypeError, ValueError, ct.ConstructError) as e:
        raise SerializeError(str(e))


def add_new_names(names_map: NamesMapT, section: Section):
    for name in section.names():
        if name not in names_map:
            names_map[name] = len(names_map)


def add_new_strings(names_map: NamesMapT, section: Section):
    for item in section.bfs_sorted_pairs():
        value = item[1]
        if isinstance(value, Str):
            if value not in names_map:
                names_map[value] = len(names_map)


def update_names_map(names_map: NamesMapT, section: Section):
    add_new_names(names_map, section)
    add_new_strings(names_map, section)


def serialize_names(names: NamesT, ostream):
    """Сборка имен в поток."""

    try:
        Names.build_stream(names, ostream)
    except (TypeError, ValueError, ct.ConstructError) as e:
        raise SerializeError(str(e))
