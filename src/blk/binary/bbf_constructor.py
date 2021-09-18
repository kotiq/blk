"""Только для версии 3."""

import io
import typing as t
import zlib
import construct as ct
from construct import this, len_
from blk.types import *
from .constants import *
from .constructor import getvalue, VT
from .error import *
from .typed_named_tuple import TypedNamedTuple

__all__ = ['compose_bbf', 'compoze_bbf_zlib', 'serialize_bbf', 'serialize_bbf_zlib']


class Version(ct.SymmetricAdapter):
    def _decode(self, obj: t.Tuple[int, int], context: ct.Container, path: str) -> t.Tuple[int, int]:
        hi, lo = obj
        if hi != 3:
            raise ct.ValidationError("Поддерживается только версия 3: {}".format(hi))
        return obj


@ct.singleton
class VLQ(ct.Construct):
    """
    Целое переменной длины.

    Маска старшего байта 0x3f. Длина кодируется первой парой битов:\n
    0b0xxx_xxxx, 1 байтовое Int7ub\n
    0b10xx_xxxx_yyyy_yyyy, 2 байтовое Int14ub\n
    0b11xx_xxxx_yyyy_yyyy_zzzz_zzzz, 3 байтовое int22ub\n
    Откуда максимальная длина строки 2**22 - 1 = 0x3f_ffff байтов.
    """

    def _parse(self, stream: io.BufferedIOBase, context: ct.Container, path: str) -> int:
        head = ct.Byte._parsereport(stream, context, path)
        if (head & 0x80) == 0:
            return head
        elif (head & 0xc0) == 0x80:
            tail = ct.Byte._parsereport(stream, context, path)
            return ((head & 0x3f) << 8) | tail
        else:
            tail = ct.Short._parsereport(stream, context, path)
            return ((head & 0x3f) << 16) | tail

    def _build(self, obj: int, stream: io.BufferedIOBase, context: ct.Container, path: str) -> int:
        if obj < 0:
            raise ct.IntegerError('Отрицательное число: {}'.format(obj))
        elif obj < 0x80:
            ct.Byte._build(obj, stream, context, path)
        elif obj < 0x40_00:
            ct.Short._build(0x80_00 | obj, stream, context, path)
        elif obj < 0x40_00_00:
            ct.Int24ub._build(0xc0_00_00 | obj, stream, context, path)
        else:
            raise ct.IntegerError('Число велико для Int22: {}'.format(obj))
        return obj


RawPascalString = ct.Prefixed(VLQ, ct.GreedyBytes).compile()

String = ct.ExprAdapter(
    RawPascalString,
    lambda obj, ctx: Str.of(obj),
    lambda obj, ctx: obj.encode()
).compile()

Offset = ct.Int32ul.compile()

types_cons_map = {
    UByte: ct.Byte.compile(),
    Int: ct.Int32sl.compile(),
    Long: ct.Int64sl.compile(),
    Float: ct.Float32l.compile(),
}

for c in (Float12, Float4, Float3, Float2, Color, Int3, Int2):
    types_cons_map[c] = (types_cons_map[c.type])[c.size].compile()


TagModule = ct.ByteSwapped(ct.Bitwise(ct.Struct(
    'tag' / ct.ExprValidator(ct.BitsInteger(2), lambda obj, ctx: 1 <= obj <= 3),
    'module' / ct.ExprValidator(ct.BitsInteger(14), lambda obj, ctx: obj != 0),
)))


def hash_(bs: bytes, module: int, hashes: t.Container[int]) -> int:
    # DJBX33A, модуль uint14
    h = 5381
    for b in bs:
        h = ((h << 5) + h + b) & 0xffff
    h %= module
    # коллизии
    while h in hashes:
        h += module
        # hash в дереве хранится как Int24ul
        if h > 0xff_ff_ff:
            raise ValueError("Исчерпаны значения hash: {}".format(h))
    return h


class NamesMap(dict):
    """name_id => Name"""

    def __init__(self, uniq_raw_names: t.Iterable[bytes], module: int):
        super().__init__()
        self.module = module

        for uniq_raw_name in uniq_raw_names:
            h = hash_(uniq_raw_name, module, self)
            self[h] = Name.of(uniq_raw_name)


class InvNamesMap(dict):
    """Name => name_id"""

    def __init__(self, names: t.Iterable[Name], module: int):
        super().__init__()
        self.module = module

        for name in names:
            if name in self:
                continue
            h = hash_(name.encode(), module, self.values())
            self[name] = h


class InvStrings(dict):
    """Str => index"""

    def __init__(self, strings: t.Iterable[str]):
        super().__init__()
        for string in strings:
            if string in self:
                continue
            i = len(self)
            self[string] = i


@ct.singleton
class Names(ct.Construct):
    def _parse(self, stream: io.BufferedIOBase, context: ct.Container, path: str) -> NamesMap:
        tag_module = TagModule._parsereport(stream, context, path)
        tag = tag_module.tag
        module = tag_module.module
        if tag == 1:
            names_count_con = ct.Byte
        elif tag == 2:
            names_count_con = ct.Int16ul
        elif tag == 3:
            names_count_con = ct.Int32ul
        else:
            raise ct.ValidationError('Код конструктора количества имен: {}'.format(tag))
        uniq_raw_names = ct.PrefixedArray(names_count_con, RawPascalString)._parsereport(stream, context, path)
        return NamesMap(uniq_raw_names, module)

    def _build(self, obj: InvNamesMap,
               stream: io.BufferedIOBase, context: ct.Container, path: str) -> InvNamesMap:
        module = obj.module
        uniq_raw_names = tuple(name.encode() for name in obj)
        names_count = len(uniq_raw_names)
        if names_count < 0x1_00:
            names_count_con = ct.Byte
            tag = 1
        elif names_count < 0x1_00_00:
            names_count_con = ct.Int16ul
            tag = 2
        elif names_count < 0x1_00_00_00_00:
            names_count_con = ct.Int32ul
            tag = 3
        else:
            raise ct.ValidationError('Слишком большое количество имен: {}'.format(names_count))
        TagModule._build(dict(tag=tag, module=module), stream, context, path)
        ct.PrefixedArray(names_count_con, RawPascalString)._build(uniq_raw_names, stream, context, path)
        return obj


TagSize = ct.ByteSwapped(ct.Bitwise(ct.Struct(
    'tag' / ct.ExprValidator(ct.BitsInteger(2), lambda obj, ctx: 0 <= obj <= 3),
    'size' / ct.BitsInteger(30)
)))


@ct.singleton
class Strings(ct.Construct):
    def _parse(self, stream: io.BufferedIOBase, context: ct.Container, path: str) -> t.List[Name]:
        tag_size = TagSize._parsereport(stream, context, path)
        tag = tag_size.tag
        strings_data_size = tag_size.size
        if tag == 0:
            return []
        elif tag == 1:
            strings_count_con = ct.Byte
        elif tag == 2:
            strings_count_con = ct.Int16ul
        elif tag == 3:
            strings_count_con = ct.Int32ul
        else:
            raise ct.ValidationError('Код конструктора количества строк: {}'.format(tag))
        strings_count = strings_count_con._parsereport(stream, context, path)
        strings_data_stream = io.BytesIO(ct.stream_read(stream, strings_data_size))
        strings = String[strings_count]._parsereport(strings_data_stream, context, path)
        return strings

    def _build(self, obj: t.Mapping[Str, int],
               stream: io.BufferedIOBase, context: ct.Container, path: str) -> t.Collection[Str]:
        strings_count = len(obj)
        if strings_count == 0:
            strings_count_con = ct.Error
            tag = 0
        elif strings_count < 0x1_00:
            strings_count_con = ct.Byte
            tag = 1
        elif strings_count < 0x1_00_00:
            strings_count_con = ct.Int16ul
            tag = 2
        elif strings_count < 0x1_00_00_00_00:
            strings_count_con = ct.Int32ul
            tag = 3
        else:
            raise ct.ValidationError('Слишком большое количество строк: {}'.format(strings_count))

        if tag == 0:
            size = 0
            TagSize._build(dict(tag=tag, size=size), stream, context, path)
        else:
            strings_data_stream = io.BytesIO()
            String[strings_count]._build(obj, strings_data_stream, context, path)
            size = strings_data_stream.seek(0, io.SEEK_END)
            TagSize._build(dict(tag=tag, size=size), stream, context, path)
            strings_count_con._build(strings_count, stream, context, path)
            ct.stream_write(stream, strings_data_stream.getvalue(), size)
        return obj


class PartialValueInfo(t.NamedTuple):
    name_id: int
    type_id: int


PartialValueInfoCon = TypedNamedTuple(
    PartialValueInfo,
    ct.Sequence(
        'name_id' / ct.Int24ul,
        'type_id' / ct.Byte,
    )
)


class Size(t.NamedTuple):
    params_count: int
    blocks_count: int


SizeCon = TypedNamedTuple(
    Size,
    ct.Sequence(
        'params_count' / ct.Int16ul,
        'blocks_count' / ct.Int16ul,
    )
)

true_id = types_codes_map[Bool]
false_id = 0x80 | true_id


@ct.singleton
class Block(ct.Construct):
    def _parse(self, stream: io.BufferedIOBase, context: ct.Container, path: str) -> Section:
        names: t.Mapping[int, Name] = context.names
        strings: t.Sequence[Str] = context.strings
        root = Section()
        params_count, blocks_count = SizeCon._parsereport(stream, context, path)
        partial_params_info = PartialValueInfoCon[params_count]._parsereport(stream, context, path)

        for name_id, type_id in partial_params_info:
            if type_id == false_id:
                value = false
            elif type_id == true_id:
                value = true
            else:
                cls = codes_types_map[type_id]
                if issubclass(cls, Section):
                    raise ValueError('Ожидался код параметра: {}'.format(type_id))
                elif issubclass(cls, Str):
                    str_id = Offset._parsereport(stream, context, path)
                    value = strings[str_id]
                else:
                    con = types_cons_map[cls]
                    value = cls(con._parsereport(stream, context, path))
            name = names[name_id]
            root.append(name, value)

        for _ in range(blocks_count):
            name_id, type_id = PartialValueInfoCon._parsereport(stream, context, path)
            cls = codes_types_map[type_id]
            if not issubclass(cls, Section):
                raise ValueError('Ожидался код секции: {}'.format(type_id))
            value = Block._parsereport(stream, context, path)  # @r
            name = names[name_id]
            root.append(name, value)

        return root

    def _build(self, obj: Section, stream: io.BufferedIOBase, context: ct.Container, path: str) -> Section:
        inv_names_map: t.Mapping[Name, int] = context.names
        inv_strings: t.Mapping[Str, int] = context.strings

        splitted_values = (param_pairs, section_pairs) = obj.split_values()
        size = Size(*map(len, splitted_values))
        SizeCon._build(size, stream, context, path)
        for name, param in param_pairs:
            if param is true:
                type_id = true_id
            elif param is false:
                type_id = false_id
            else:
                cls = param.__class__
                type_id = types_codes_map[cls]
            name_id = inv_names_map[name]
            PartialValueInfoCon._build(PartialValueInfo(name_id, type_id), stream, context, path)

        for name, param in param_pairs:
            cls = param.__class__
            if not isinstance(param, Bool):
                if isinstance(param, Str):
                    con = Offset
                    value = inv_strings[param]
                else:
                    con = types_cons_map[cls]
                    value = param
                con._build(value, stream, context, path)

        for name, section_ in section_pairs:
            name_id = inv_names_map[name]
            type_id = types_codes_map[Section]
            PartialValueInfoCon._build(PartialValueInfo(name_id, type_id), stream, context, path)
            self._build(section_, stream, context, path)  # @r

        return obj


Data = ct.FocusedSeq(
    'block',
    'names' / ct.Aligned(4, ct.Rebuild(Names, lambda ctx: InvNamesMap(ctx.block.names(), ctx._._.module))),
    'strings' / ct.Aligned(4, ct.Rebuild(Strings, lambda ctx: InvStrings(ctx.block.strings()))),
    'block' / Block)

BBFFile = ct.FocusedSeq(
    'data',
    ct.Const(b'\x00BBF'),
    'version' / ct.Rebuild(Version(ct.Int16ul[2]), this._.version),
    'data' / ct.Prefixed(ct.Int32ul, Data)
)


class ZlibCompressed(ct.Tunnel):
    def __init__(self, subcon,
                 level: VT[int] = -1,
                 max_length: VT[int] = 0,
                 ):
        super().__init__(subcon)
        self.level = level
        self.max_length = max_length

    def _decode(self, data, context, path):
        max_lenght = getvalue(self.max_length, context)
        dctx = zlib.decompressobj()
        return dctx.decompress(data, max_lenght)

    def _encode(self, data, context, path):
        level = getvalue(self.level, context)
        cctx = zlib.compressobj(level)
        return cctx.compress(data)


CompressedBBFFile = ct.FocusedSeq(
    'data_bs',
    ct.Const(b'\x00BBz'),
    'size' / ct.Rebuild(ct.Int32ul, len_(this.data_bs)),
    'data_bs' / ct.Prefixed(ct.Int32ul, ZlibCompressed(ct.GreedyBytes, max_length=this.size)),
)


# todo: readable/writable protocol
def compose_bbf(istream: t.BinaryIO) -> Section:
    """Сборка секции из потока."""

    try:
        return BBFFile.parse_stream(istream)
    except (TypeError, ValueError, KeyError, ct.ConstructError) as e:
        raise ComposeError(e)


def serialize_bbf(section: Section, ostream: t.BinaryIO, version: t.Tuple[int, int] = (3, 1), module: int = 0x100):
    try:
        return BBFFile.build_stream(section, ostream, version=version, module=module)
    except (TypeError, ValueError, ct.ConstructError) as e:
        raise SerializeError(str(e))


def compoze_bbf_zlib(istream: t.BinaryIO) -> Section:
    """Сборка секции из сжатого потока."""

    try:
        data_bs = CompressedBBFFile.parse_stream(istream)
        return BBFFile.parse(data_bs)
    except (TypeError, ValueError, ct.ConstructError, zlib.error) as e:
        raise ComposeError(str(e))


def serialize_bbf_zlib(section: Section, ostream: t.BinaryIO, version: t.Tuple[int, int] = (3, 1), module: int = 0x100):
    try:
        data_bs = BBFFile.build(section, version=version, module=module)
        CompressedBBFFile.build_stream(data_bs, ostream)
    except (TypeError, ValueError, ct.ConstructError, zlib.error) as e:
        raise SerializeError(str(e))
