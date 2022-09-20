from io import BytesIO
from hashlib import sha1, sha256
from collections import OrderedDict
from typing import (Any, BinaryIO, Callable, Container, Iterable, Mapping, MutableSequence, NamedTuple, Optional,
                    OrderedDict as ODict, Sequence, Tuple, Type, TypeVar, Union)
import construct as ct
from construct import len_, this
from zstandard import FLUSH_FRAME, ZstdCompressor, ZstdDecompressor, ZstdError
from blk.types import (Bool, Color, DictSection, Float, Float2, Float3, Float4, Float12, Int, Int2, Int3, Long, Name,
                       Parameter, Section, Str, UByte, Var, Value, false, true)
from .constants import BlkType, codes_types_map, types_codes_map
from .error import ComposeError, SerializeError
from .typed_named_tuple import TypedNamedTuple

__all__ = [
    'Fat',
    'InvNames',
    'NamesFile',
    'NO_DICT_EXPECTED',
    'compose_fat',
    'compose_names',
    'compose_partial_fat',
    'compose_partial_fat_zst',
    'compose_partial_names',
    'compose_partial_slim',
    'compose_partial_slim_zst',
    'compose_slim',
    'compose_slim_zst',
    'compose_slim_zst_dict',
    'serialize_fat',
    'serialize_fat_zst',
    'serialize_partial_fat',
    'serialize_slim',
    'serialize_names',
    'serialize_partial_names',
    'serialize_partial_slim',
    'serialize_slim_zst',
    'serialize_slim_zst_dict',
]

NO_DICT_EXPECTED = b'\x00'*32

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

NameStr = Union[Name, Str]
NamesSeq = Sequence[NameStr]
NamesIt = Iterable[NameStr]
NamesMap = ODict[NameStr, int]


class InvNames(OrderedDict):
    """Name => name_id"""

    def __init__(self, names: Iterable[Union[Name, Str]] = None) -> None:
        super().__init__()
        if names:
            for i, name in enumerate(names):
                self[name] = i

    @classmethod
    def of(cls, section: DictSection, include_strings: bool = True) -> 'InvNames':
        inst = InvNames()
        inst.update_(section, include_strings)
        return inst

    def update_(self, section: DictSection, include_strings: bool):
        self.add_names(section)
        if include_strings:
            self.add_strings(section)

    def add_names(self, section: DictSection):
        for name in section.names():
            if name not in self:
                self[name] = len(self)

    def add_strings(self, section: DictSection):
        for item in section.bfs_sorted_pairs():
            value = item[1]
            if isinstance(value, Str):
                if value not in self:
                    self[value] = len(self)


class NamesAdapter(ct.Adapter):
    def _decode(self, obj: Optional[NamesSeq], context: Container, path: str) -> NamesSeq:
        return () if obj is None else obj

    def _encode(self, obj: NamesMap, context: Container, path: str) -> NamesIt:
        return obj.keys()


Names = NamesAdapter(NamesCon)

TaggedOffset = ct.ByteSwapped(ct.Bitwise(ct.Sequence(ct.Bit, ct.BitsInteger(31)))).compile()


class ParamInfo(NamedTuple):
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


class BlockInfo(NamedTuple):
    name_id: int
    params_count: int
    blocks_count: int
    block_offset: Optional[int]


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

Pair = Tuple[Name, Value]
LongValue = Union[Str, Float12, Float4, Float3, Float2, Int3, Int2, Long]
LongValueType = Union[Type[Str], Type[Float12], Type[Float4], Type[Float3], Type[Float2], Type[Int3], Type[Int2],
                      Type[Long]]
ParametersMap = ODict[Union[Name, LongValue], int]
ValuesMap = Mapping[LongValueType, ParametersMap]
ParameterInfo = Tuple[int, int, bytes]
ParameterInfos = MutableSequence[ParameterInfo]
BlockInfoT = Tuple[int, int, int, Optional[int]]
BlockInfos = MutableSequence[BlockInfoT]
ParameterT = Tuple[Name, Parameter]
Parameters = MutableSequence[ParameterT]
SectionT = Tuple[Optional[Name], DictSection]
Sections = MutableSequence[SectionT]
T = TypeVar('T')
VT = Union[T, Callable[[ct.Container], T]]


class BlockAdapter(ct.Adapter):
    def __init__(self, subcon,
                 names_or_inv_names: VT[Union[NamesSeq, NamesIt, InvNames]],
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

    def parse_params_data(self, con: ct.Construct, offset) -> Any:
        self.params_data.seek(offset)
        return con.parse_stream(self.params_data)

    def build_params_data(self, con: ct.Construct, value) -> int:
        offset = self.params_data.tell()
        con.build_stream(value, self.params_data)
        return offset

    def _decode(self, obj: ct.Container, context, path) -> DictSection:
        names: NamesSeq = ct.evaluate(self.names_or_inv_names, context)

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
            value = DictSection()
            blocks.append((name, value))

        for (_, params_count, blocks_count, block_offset), (_, section) in zip(obj.blocks, blocks):
            start = param_offset
            end = start + params_count
            for name, value in params[start:end]:
                section.append((name, value))
            param_offset = end

            if blocks_count:
                start = block_offset
                end = start + blocks_count
                for name, value in blocks[start:end]:
                    section.append((name, value))

        return blocks[0][1]

    def _encode(self, obj: DictSection, context, path) -> ct.Container:
        inv_names: InvNames = ct.evaluate(self.names_or_inv_names, context)
        self._strings_in_names = ct.evaluate(self.strings_in_names, context)
        external_names = ct.evaluate(self.external_names, context)
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
    'header' / ct.Const(BlkType.FAT, ct.Byte),
    'names' / ct.Rebuild(Names, lambda ctx: InvNames.of(ctx.block, ctx._params.strings_in_names)),
    'block' / BlockAdapter(BlockCon, this.names, lambda ctx: ctx._params.strings_in_names),
)

Slim = ct.FocusedSeq(
    'block',
    'header' / ct.Const(BlkType.SLIM, ct.Byte),
    'names' / ct.Rebuild(Names, {}),
    'block' / BlockAdapter(BlockCon, lambda ctx: ctx._params.names_or_inv_names, True, True),
)


def compose_partial_fat(istream: BinaryIO) -> DictSection:
    """
    Сборка секции из потока со встроенными именами.
    Входной поток не содержит первого байта 0x01.

    :param istream: входной поток
    :return: секция
    :raises ComposeError: ошибка при распаковке
    """

    try:
        names = Names.parse_stream(istream)
        return BlockAdapter(BlockCon, names).parse_stream(istream)
    except (TypeError, ValueError, ct.ConstructError) as e:
        raise ComposeError(str(e))


def compose_partial_fat_zst(istream: BinaryIO, dctx: ZstdDecompressor) -> DictSection:
    """
    Сборка секции из потока со встроенными именами.
    Входной поток не содержит первого байта 0x02.

    :param istream: входной поток
    :param dctx: декомпрессор
    :return: секция
    :raises ComposeError: ошибка при распаковке
    """

    try:
        size = ct.Int24ul.parse_stream(istream)
        zstd_istream = dctx.stream_reader(istream)
        return compose_fat(zstd_istream)
    except (ct.ConstructError, ZstdError) as e:
        raise ComposeError(str(e))


def compose_fat(istream: BinaryIO) -> DictSection:
    try:
        ct.Const(BlkType.FAT, ct.Byte).parse_stream(istream)
    except ct.ConstructError as e:
        raise ComposeError(str(e))

    return compose_partial_fat(istream)


# todo: remove
def serialize_partial_fat(section: DictSection, ostream: BinaryIO, strings_in_names: bool = False) -> None:
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


def serialize_fat(section: DictSection, ostream: BinaryIO, strings_in_names: bool = False) -> None:
    try:
        ct.Byte.build_stream(BlkType.FAT, ostream)
    except ct.ConstructError as e:
        raise SerializeError(str(e))

    serialize_partial_fat(section, ostream, strings_in_names)


def serialize_fat_zst(section: DictSection, cctx: ZstdCompressor, ostream: BinaryIO, strings_in_names: bool = False) -> None:
    try:
        ct.Byte.build_stream(BlkType.FAT_ZST, ostream)
        fat_stream = BytesIO()
        serialize_fat(section, fat_stream, strings_in_names)
        zstd_data = cctx.compress(fat_stream.getvalue())
        ct.Prefixed(ct.Int24ul, ct.GreedyBytes).build_stream(zstd_data, ostream)

    except (ct.ConstructError, ZstdError) as e:
        raise SerializeError(str(e))


def compose_partial_slim(names: NamesSeq, istream: BinaryIO) -> DictSection:
    """
    Сборка секции из потока. Имена в списке.
    Входной поток не содержит первого байта 0x03.

    :param names: общие имена или строки
    :param istream: входной поток
    :return: секция
    """

    try:
        Names.parse_stream(istream)
        return BlockAdapter(BlockCon, names).parse_stream(istream)
    except (TypeError, ValueError, ct.ConstructError) as e:
        raise ComposeError(str(e))


def compose_slim(names: NamesSeq, istream: BinaryIO) -> DictSection:
    try:
        ct.Const(BlkType.SLIM, ct.Byte).parse_stream(istream)
    except ct.ConstructError as e:
        raise ComposeError(str(e))

    return compose_partial_slim(names, istream)


def compose_partial_slim_zst(names: NamesSeq, istream: BinaryIO, dctx: ZstdDecompressor) -> DictSection:
    try:
        zstd_stream = dctx.stream_reader(istream)
        return compose_partial_slim(names, zstd_stream)
    except ZstdError as e:
        raise ComposeError(str(e))


def compose_slim_zst(names: NamesSeq, istream: BinaryIO, dctx: ZstdDecompressor) -> DictSection:
    try:
        ct.Const(BlkType.SLIM_ZST, ct.Byte).parse_stream(istream)
    except ct.ConstructError as e:
        raise ComposeError(str(e))

    return compose_partial_slim_zst(names, istream, dctx)


def compose_slim_zst_dict(names: NamesSeq, istream: BinaryIO, dctx: ZstdDecompressor) -> DictSection:
    try:
        ct.Const(BlkType.SLIM_ZST_DICT, ct.Byte).parse_stream(istream)
    except ct.ConstructError as e:
        raise ComposeError(str(e))

    return compose_partial_slim_zst(names, istream, dctx)


def compose_partial_names(istream: BinaryIO) -> NamesSeq:
    """
    Сборка списка имен из потока.
    Входной поток не содержит идентификаторов карты и словаря (первые 40 байт).

    :param istream: входной поток
    :return: имена или строки
    :raises ComposeError: Ошибка при построении карты имен
    """

    try:
        return Names.parse_stream(istream)
    except (TypeError, ValueError, ct.ConstructError) as e:
        raise ComposeError(str(e))


class NamesFile(NamedTuple):
    table_digest: bytes
    dict_digest: bytes
    names: NamesSeq


# todo: NamesFileCon
def compose_names(istream: BinaryIO, dctx: ZstdDecompressor) -> NamesFile:
    """
    Сборка карты имен из входного потока.

    :param istream: входной поток
    :param dctx: декомпрессор
    :return: пространство имен для файла имен
    :raises ComposeError: ошибка при построении карты имен
    """

    try:
        table_digest = ct.stream_read(istream, 8)
        dict_digest = ct.stream_read(istream, 32)
        zstd_istream = dctx.stream_reader(istream)
        names = compose_partial_names(zstd_istream)
        return NamesFile(table_digest, dict_digest, names)
    except (ct.ConstructError, ZstdError) as e:
        raise ComposeError(str(e))


# todo: remove
def serialize_partial_slim(section: DictSection, inv_names: InvNames, ostream: BinaryIO) -> None:
    """Сборка секции с именами из отображения в поток.
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


def serialize_slim(section: DictSection, inv_names: InvNames, ostream: BinaryIO) -> None:
    try:
        ct.Byte.build_stream(BlkType.SLIM, ostream)
    except ct.ConstructError as e:
        raise SerializeError(str(e))

    serialize_partial_slim(section, inv_names, ostream)


def serialize_slim_zst(section: DictSection, inv_names: InvNames, cctx: ZstdCompressor, ostream: BinaryIO) -> None:
    try:
        ct.Byte.build_stream(BlkType.SLIM_ZST, ostream)
        zstd_ostream = cctx.stream_writer(ostream)
        serialize_partial_slim(section, inv_names, zstd_ostream)
        zstd_ostream.flush(FLUSH_FRAME)
    except ZstdError as e:
        raise SerializeError(str(e))


def serialize_slim_zst_dict(section: DictSection, inv_names: InvNames, cctx: ZstdCompressor, ostream: BinaryIO) -> None:
    try:
        ct.Byte.build_stream(BlkType.SLIM_ZST_DICT, ostream)
        zstd_ostream = cctx.stream_writer(ostream)
        serialize_partial_slim(section, inv_names, zstd_ostream)
        zstd_ostream.flush(FLUSH_FRAME)
    except ZstdError as e:
        raise SerializeError(str(e))


# todo: remove
def serialize_partial_names(inv_names: NamesMap, ostream) -> None:
    """Сборка имен в поток."""

    try:
        Names.build_stream(inv_names, ostream)
    except (TypeError, ValueError, ct.ConstructError) as e:
        raise SerializeError(str(e))


def serialize_names(inv_names: NamesMap, dict_digest: bytes, cctx: ZstdCompressor, ostream: BinaryIO) -> None:
    """Сборка карты имен в поток.

    :param inv_names: таблица имен (name => index)
    :param dict_digest: идентификатор словаря
    :param cctx: компрессор
    :param ostream: выходной поток
    :raises SerializeError: ошибка при построении файла карты имен.
    """

    try:
        tmp = BytesIO()
        Names.build_stream(inv_names, tmp)
        # Алгоритм получения table_id я не знаю. Пусть будет 16 первых символов от sha1 дайджеста.
        buf = tmp.getbuffer()
        table_digest = sha1(buf).digest()[:8]
        ct.stream_write(ostream, table_digest, 8)
        ct.stream_write(ostream, dict_digest, 32)
        zstd_ostream = cctx.stream_writer(ostream)
        ct.stream_write(zstd_ostream, bytes(buf), len(buf))
        zstd_ostream.flush(FLUSH_FRAME)
    except (TypeError, ValueError, ct.ConstructError, ZstdError) as e:
        raise SerializeError(str(e))
