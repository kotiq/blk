from io import BytesIO
from collections import OrderedDict
import typing as t
import construct as ct
from construct import len_, this
from blk.types import *
from .constants import *
from .error import *
from .typed_named_tuple import TypedNamedTuple

__all__ = ['serialize_fat_data', 'compose_fat_data', 'compose_names_data', 'compose_slim_data', 'serialize_slim_data',
           'serialize_names_data', 'InvNames', 'compose_fat', 'serialize_fat', 'Fat']

RawCString = ct.NullTerminated(ct.GreedyBytes).compile()

NameCon = ct.ExprAdapter(
    RawCString,
    lambda obj, ctx: Name.of(obj),
    lambda obj, ctx: obj.encode()
).compile()

String = ct.ExprAdapter(
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
}

types_cons_map[Color] = ct.ExprSymmetricAdapter(
    (types_cons_map[Color.type])[Color.size],
    lambda o, _: tuple(reversed(o[:-1])) + (o[-1], ),
).compile()

for c in (Float12, Float4, Float3, Float2, Int3, Int2):
    types_cons_map[c] = (types_cons_map[c.type])[c.size].compile()

NamesCon = ct.FocusedSeq(
    'names',
    'names_count' / ct.Rebuild(ct.VarInt, ct.len_(ct.this.names)),
    'names' / ct.If(this.names_count,
                    ct.Prefixed(ct.VarInt, NameCon[ct.this.names_count]))
).compile()

NameStr = t.Union[Name, Str]
NamesSeq = t.Sequence[NameStr]
NamesIt = t.Iterable[NameStr]
NamesMap = t.OrderedDict[NameStr, int]


class InvNames(OrderedDict):
    """Name => name_id"""

    def __init__(self, names: t.Iterable[t.Union[Name, Str]] = None):
        super().__init__()
        if names:
            for i, name in enumerate(names):
                self[name] = i

    @classmethod
    def of(cls, section: Section, include_strings: bool = True) -> 'InvNames':
        inst = InvNames()
        inst.update_(section, include_strings)
        return inst

    def update_(self, section: Section, include_strings: bool):
        self.add_names(section)
        if include_strings:
            self.add_strings(section)

    def add_names(self, section: Section):
        for name in section.names():
            if name not in self:
                self[name] = len(self)

    def add_strings(self, section: Section):
        for item in section.bfs_sorted_pairs():
            value = item[1]
            if isinstance(value, Str):
                if value not in self:
                    self[value] = len(self)


class NamesAdapter(ct.Adapter):
    def _decode(self, obj: t.Optional[NamesSeq], context: t.Container, path: str) -> NamesSeq:
        return () if obj is None else obj

    def _encode(self, obj: NamesMap, context: t.Container, path: str) -> NamesIt:
        return obj.keys()


Names = NamesAdapter(NamesCon)

TaggedOffset = ct.ByteSwapped(ct.Bitwise(ct.Sequence(ct.Bit, ct.BitsInteger(31)))).compile()


class ParamInfo(t.NamedTuple):
    name_id: int
    type_id: int
    data: bytes


ParamInfoCon = TypedNamedTuple(
    ParamInfo,
    ct.Sequence(
        'name_id' / ct.Int24ul,
        'type_id' / ct.Byte,
        'data' / ct.Bytes(4)
    )
).compile()

Id_of_root = None


class BlockInfo(t.NamedTuple):
    name_id: int
    params_count: int
    blocks_count: int
    block_offset: t.Optional[int]


BlockInfoCon = TypedNamedTuple(
    BlockInfo,
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


BlockCon = """Структура файла, за исключением таблицы имен имен""" * ct.Struct(
    'blocks_count' / ct.Rebuild(ct.VarInt, len_(this.blocks)),
    'params_count' / ct.Rebuild(ct.VarInt, len_(this.params)),
    'params_data' / ct.Prefixed(ct.VarInt, ct.GreedyBytes),
    'params' / ParamInfoCon[this.params_count],
    'blocks' / BlockInfoCon[this.blocks_count],
).compile()

Pair = t.Tuple[Name, Value]
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
T = t.TypeVar('T')
VT = t.Union[T, t.Callable[[ct.Container], T]]


def getvalue(val: VT[T], context) -> T:
    return val(context) if callable(val) else val


class BlockAdapter(ct.Adapter):
    def __init__(self, subcon,
                 names_or_inv_names: VT[t.Union[NamesSeq, NamesIt, InvNames]],
                 strings_in_names: VT[bool] = False,
                 external_names: VT[bool] = False
                 ):
        """
        names: int => Name для разбора
        inv_names: Name => int для построения
        """

        super().__init__(subcon)
        self.params_data: BytesIO = ...

        self.names_or_inv_names = names_or_inv_names
        self.strings_in_names = strings_in_names
        self._strings_in_names: bool = ...
        self.external_names = external_names

    def parse_params_data(self, con: ct.Construct, offset) -> t.Any:
        self.params_data.seek(offset)
        return con.parse_stream(self.params_data)

    def build_params_data(self, con: ct.Construct, value) -> int:
        offset = self.params_data.tell()
        con.build_stream(value, self.params_data)
        return offset

    def _decode(self, obj: ct.Container, context, path) -> Section:
        names: NamesSeq = getvalue(self.names_or_inv_names, context)

        self.params_data = BytesIO(obj.params_data)
        params: Parameters = []
        blocks: Sections = []
        param_offset = 0

        for name_id, type_id, data in obj.params:
            name = names[name_id]
            cls = codes_types_map[type_id]

            if cls is Str:
                tag, offset = TaggedOffset.parse(data)
                init = names[offset] if tag else self.parse_params_data(String, offset)
                value = cls.of(init)
            else:
                con = types_cons_map[cls]
                if cls in (Float12, Float4, Float3, Float2, Int3, Int2, Long):
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
        inv_names: InvNames = getvalue(self.names_or_inv_names, context)
        self._strings_in_names = getvalue(self.strings_in_names, context)
        external_names = getvalue(self.external_names, context)
        if external_names:
            inv_names.update_(obj, include_strings=True)

        self.params_data = BytesIO()
        params: ParameterInfos = []
        blocks: BlockInfos = []
        block_offset_var = Var(0)

        values_maps: ValuesMap = dict((cls, OrderedDict())
                                      for cls in (Str, Float12, Float4, Float3, Float2, Int2, Int3, Long))
        """value -> offset"""

        if not self._strings_in_names:
            map_ = values_maps[Str]
            for _, value in obj.bfs_sorted_pairs():
                if isinstance(value, Str) and (value not in map_):
                    map_[value] = self.build_params_data(String, value)

            pos = self.params_data.tell()
            pad = -pos % 4
            self.params_data.write(b'\x00'*pad)

        for item in obj.bfs_sorted_pairs():
            self.build_item(item, inv_names, values_maps, params, blocks, block_offset_var)

        return {
            'params_data': self.params_data.getvalue(),
            'params': params,
            'blocks': blocks
        }

    def build_item(self, item: Pair, inv_names: NamesMap, values_maps: ValuesMap,
                   params: ParameterInfos, blocks: BlockInfos, block_offset_var: Var):
        name, value = item
        name_id = inv_names.get(name, Name.of_root)

        if isinstance(value, Parameter):
            cls = value.__class__
            code = types_codes_map[cls]

            if cls is Str:
                if self._strings_in_names:
                    map_ = inv_names
                    tag = 1
                else:
                    map_ = values_maps[cls]
                    tag = 0
                offset = map_[value]
                data = TaggedOffset.build([tag, offset])
            else:
                con = types_cons_map[cls]
                if cls in (Float12, Float4, Float3, Float2, Int3, Int2, Long):
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


Fat = ct.FocusedSeq(
    'block',
    'header' / ct.Const(1, ct.Byte),
    'names' / ct.Rebuild(Names, lambda ctx: InvNames.of(ctx.block, ctx._params.strings_in_names)),
    'block' / BlockAdapter(BlockCon, this.names, lambda ctx: ctx._params.strings_in_names),
)


def compose_fat_data(istream: t.BinaryIO) -> Section:
    """
    Сборка секции из потока со встроенными именами.

    :param istream: входной поток
    :return: секция
    """

    try:
        names = Names.parse_stream(istream)
        return BlockAdapter(BlockCon, names).parse_stream(istream)
    except (TypeError, ValueError, ct.ConstructError) as e:
        raise ComposeError(str(e))


def compose_fat(istream: t.BinaryIO) -> Section:
    try:
        ct.Const(b'\x01').parse_stream(istream)
    except ct.ConstructError as e:
        raise ComposeError(str(e))

    return compose_fat_data(istream)


def serialize_fat_data(section: Section, ostream: t.BinaryIO, strings_in_names: bool = False):
    """Дамп секции со встроенными именами в поток.

    :param section: секция
    :param ostream: выходной поток
    :param strings_in_names: значения строковых параметров находятся в своем блоке или в блоке имен.
    :return:
    """

    inv_names = InvNames.of(section, strings_in_names)
    try:
        Names.build_stream(inv_names, ostream)
        BlockAdapter(BlockCon, inv_names, strings_in_names).build_stream(section, ostream)
    except (TypeError, ValueError, ct.ConstructError) as e:
        raise SerializeError(str(e))


def serialize_fat(section: Section, ostream: t.BinaryIO, strings_in_names: bool = False):
    try:
        ct.Const(b'\x01').build_stream(None, ostream)
    except ct.ConstructError as e:
        raise SerializeError(str(e))

    serialize_fat_data(section, ostream, strings_in_names)


def compose_slim_data(names: NamesSeq, istream: t.BinaryIO) -> Section:
    """
    Сборка секции из потока. Имена в списке.

    :param names: общие имена или строки
    :param istream: входной поток
    :return: секция
    """

    try:
        Names.parse_stream(istream)
        return BlockAdapter(BlockCon, names).parse_stream(istream)
    except (TypeError, ValueError, ct.ConstructError) as e:
        raise ComposeError(str(e))


def compose_names_data(istream: t.BinaryIO) -> NamesSeq:
    """
    Сборка списка имен из потока.

    :param istream: входной поток
    :return: имена или строки
    """

    try:
        return Names.parse_stream(istream)
    except (TypeError, ValueError, ct.ConstructError) as e:
        raise ComposeError(str(e))


def serialize_slim_data(section: Section, inv_names: InvNames, ostream: t.BinaryIO):
    """Сборка секции c именами из отображения в поток.
    Отображение имен может расширяться.
    Все строковые параметры находятся в блоке имен.

    :param section: секция
    :param inv_names: отображение имя или строка => индекс
    :param ostream:
    :return:
    """

    try:
        Names.build_stream({}, ostream)
        BlockAdapter(BlockCon, inv_names, True, True).build_stream(section, ostream)
    except (TypeError, ValueError, ct.ConstructError) as e:
        raise SerializeError(str(e))


def serialize_names_data(inv_names: NamesMap, ostream):
    """Сборка имен в поток."""

    try:
        Names.build_stream(inv_names, ostream)
    except (TypeError, ValueError, ct.ConstructError) as e:
        raise SerializeError(str(e))
