"""Только для версии 3."""

import io
import typing as t
import construct as ct
from construct import this
from blk.types import *
from .constants import *
from .error import *
from .typed_named_tuple import TypedNamedTuple

__all__ = ['compose_bbf', 'compoze_bbz', 'serialize_bbf', 'serialize_bbz']


class Version(ct.Adapter):
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


class NamesMapInitContainer(t.NamedTuple):
    raw_names: t.List[bytes]
    module: int


@ct.singleton
class NamesMapInit(ct.Construct):
    def _parse(self, stream: io.BufferedIOBase, context: ct.Container, path: str) -> NamesMapInitContainer:
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
        raw_names = ct.PrefixedArray(names_count_con, RawPascalString)._parsereport(stream, context, path)
        return NamesMapInitContainer(raw_names, module)

    def _build(self, obj: NamesMapInitContainer, stream: io.BufferedIOBase, context: ct.Container, path: str) -> NamesMapInitContainer:
        module = obj.module
        names = obj.raw_names
        names_count = len(obj.raw_names)
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
        ct.PrefixedArray(names_count_con, RawPascalString)._build(names, stream, context, path)
        return obj


def create_names_map(raw_names: t.Iterable[bytes], module: int) -> t.Mapping[int, Name]:
    hashmap = {}
    for raw_name in raw_names:
        # DJBX33A, модуль uint14
        h = 5381
        for b in raw_name:
            h = ((h << 5) + h + b) & 0xffff
        h %= module
        # коллизии
        while h in hashmap:
            h += module
            # hash в дереве хранится как Int24ul
            if h > 0xff_ff_ff:
                raise ValueError("Исчерпана Dom(hashmap): {}".format(h))
        hashmap[h] = Name.of(raw_name)
    return hashmap


class NamesMapAdapter(ct.Adapter):
    def _decode(self, obj: NamesMapInitContainer, context: ct.Container, path: str) -> t.Mapping[int, Name]:
        return create_names_map(obj.raw_names, obj.module)

    def _encode(self, obj, context: ct.Container, path: str):
        raise NotImplementedError


Names = NamesMapAdapter(NamesMapInit)


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

    def _build(self, obj: t.List[Str], stream: io.BufferedIOBase, context: ct.Container, path: str
               ) -> t.List[Str]:
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


class ValueInfo(t.NamedTuple):
    name_id: int
    type_id: int
    data: t.Any


true_id = types_codes_map[Bool]
false_id = 0x80 | true_id


@ct.singleton
class Block(ct.Construct):
    def _parse(self, stream: io.BufferedIOBase, context: ct.Container, path: str) -> t.List[ValueInfo]:
        params_count, blocks_count = SizeCon._parsereport(stream, context, path)
        values_info: t.List[ValueInfo] = []
        partial_params_info = PartialValueInfoCon[params_count]._parsereport(stream, context, path)
        for name_id, type_id in partial_params_info:
            if type_id in (true_id, false_id):
                data = None
            else:
                cls = codes_types_map[type_id]
                if cls is Section:
                    raise ValueError('Ожидался код параметра: {}'.format(type_id))
                elif cls is Str:
                    con = Offset
                else:
                    con = types_cons_map[cls]
                data = con._parsereport(stream, context, path)
            values_info.append(ValueInfo(name_id, type_id, data))

        for _ in range(blocks_count):
            name_id, type_id = PartialValueInfoCon._parsereport(stream, context, path)
            cls = codes_types_map[type_id]
            if cls is not Section:
                raise ValueError('Ожидался код секции: {}'.format(type_id))
            data = Block._parsereport(stream, context, path)  # @r
            values_info.append(ValueInfo(name_id, type_id, data))

        return values_info


types_cons_map[Section] = Block


class DataStruct(t.NamedTuple):
    names: t.Mapping[int, Name]
    strings: t.Sequence[Str]
    block: t.Sequence[ValueInfo]


DataStructCon = TypedNamedTuple(
    DataStruct,
    ct.Sequence(
        'names' / ct.Aligned(4, Names),
        'strings' / ct.Aligned(4, Strings),
        'block' / Block)
)


def create_section(names: t.Mapping[int, Name], strings: t.Sequence[Str], block: t.Sequence[ValueInfo]) -> Section:
    root = Section()
    for name_id, type_id, data in block:
        name = names[name_id]
        if type_id == false_id:
            value = false
        elif type_id == true_id:
            value = true
        else:
            cls = codes_types_map[type_id]
            if cls is Section:
                value = create_section(names, strings, data)  # @r
            elif cls is Str:
                value = strings[data]
            else:
                value = cls(data)
        root.append(name, value)

    return root


class DataAdapter(ct.Adapter):
    def _decode(self, obj: DataStruct, context: ct.Container, path: str) -> Section:
        names: t.Mapping[int, Name] = obj.names
        strings: t.Sequence[Str] = obj.strings
        block: t.Sequence[ValueInfo] = obj.block

        return create_section(names, strings, block)


Data = DataAdapter(DataStructCon)


BBFFile = ct.FocusedSeq(
    'data',
    ct.Const(b'\x00BBF'),
    'version' / Version(ct.Int16ul[2]),
    'data' / ct.Prefixed(ct.Int32ul, Data)
)


# todo: readable/writable protocol
def compose_bbf(istream: t.BinaryIO) -> Section:
    """Сборка секции из потока."""

    try:
        return BBFFile.parse_stream(istream)
    except (TypeError, ValueError, KeyError, ct.ConstructError) as e:
        raise ComposeError(e)


def serialize_bbf(section: Section, ostream: t.BinaryIO, module: int = 0x100):
    raise NotImplementedError


def compoze_bbz(istream: t.BinaryIO) -> Section:
    raise NotImplementedError


def serialize_bbz(section: Section, ostream: t.BinaryIO, module: int = 0x100):
    raise NotImplementedError
