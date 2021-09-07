"""Только для версии 3."""

import io
import typing as t
import construct as ct
from construct import this
from blk.types import *
from .error import *

__all__ = ['compose_bbf', 'compoze_bbz', 'serialize_bbf', 'serialize_bbz']


class Version(ct.Adapter):
    def _decode(self, obj: t.Tuple[int, int], context: ct.Container, path: str) -> t.Tuple[int, int]:
        hi, lo = obj
        if hi != 3:
            raise ct.ValidationError("Поддерживается только версия 3.")
        return obj


@ct.singleton
class VQL(ct.Construct):
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
        if head < 0x80:
            return head
        elif head < 0xc0:
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


RawPascalString = ct.Prefixed(VQL, ct.GreedyBytes)

name_con = ct.ExprAdapter(
    RawPascalString,
    lambda obj, ctx: Name.of(obj),
    lambda obj, ctx: obj.encode()
).compile()

str_con = ct.ExprAdapter(
    RawPascalString,
    lambda obj, ctx: Str.of(obj),
    lambda obj, ctx: obj.encode()
).compile()

types_cons_map = {
    Name: name_con,
    Str: str_con,
}

TagModule = ct.ByteSwapped(ct.Bitwise(ct.Struct(
    'tag' / ct.ExprValidator(ct.BitsInteger(2), lambda obj, ctx: 1 <= obj <= 3),
    'module' / ct.BitsInteger(14),
)))


class NamesInit(t.NamedTuple):
    module: int
    names: t.Sequence[Name]


@ct.singleton
class Names(ct.Construct):
    def _parse(self, stream: io.BufferedIOBase, context: ct.Container, path: str) -> NamesInit:
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
        names = ct.PrefixedArray(names_count_con, types_cons_map[Name])._parsereport(stream, context, path)
        return NamesInit(module, names)

    def _build(self, obj: NamesInit, stream: io.BufferedIOBase, context: ct.Container, path: str) -> NamesInit:
        module = obj.module
        names = obj.names
        names_count = len(obj.names)
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
        ct.PrefixedArray(names_count_con, types_cons_map[Name])._build(names, stream, context, path)
        return obj


TagSize = ct.ByteSwapped(ct.Bitwise(ct.Struct(
    'tag' / ct.ExprValidator(ct.BitsInteger(2), lambda obj, ctx: 0 <= obj <= 3),
    'size' / ct.BitsInteger(30)
)))


@ct.singleton
class Strings(ct.Construct):
    def _parse(self, stream: io.BufferedIOBase, context: ct.Container, path: str) -> t.Sequence[Name]:
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
        strings = (types_cons_map[Str])[strings_count]._parsereport(strings_data_stream, context, path)
        return strings

    def _build(self, obj: t.Sequence[Str], stream: io.BufferedIOBase, context: ct.Container, path: str
               ) -> t.Sequence[Str]:
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
            (types_cons_map[Str])[strings_count]._build(obj, strings_data_stream, context, path)
            size = strings_data_stream.seek(0, io.SEEK_END)
            TagSize._build(dict(tag=tag, size=size), stream, context, path)
            strings_count_con._build(strings_count, stream, context, path)
            ct.stream_write(stream, strings_data_stream.getvalue(), size)
        return obj


FileStruct = ct.Struct(
    'names_init' / ct.Aligned(4, Names),
    'strings' / ct.Aligned(4, Strings),
    'tree' / ct.Error,
)


class FileAdapter(ct.Adapter):
    pass


BBFFile = ct.Struct(
    ct.Const(b'\x00BBF'),
    'version' / Version(ct.Int32ul[2]),
    'data' / ct.Prefixed(ct.Int32ul, ct.GreedyBytes)
)


# todo: readable/writable protocol
def compose_bbf(istream: t.BinaryIO) -> Section:
    raise NotImplementedError


def serialize_bbf(section: Section, ostream: t.BinaryIO):
    raise NotImplementedError


def compoze_bbz(istream: t.BinaryIO) -> Section:
    raise NotImplementedError


def serialize_bbz(section: Section, ostream: t.BinaryIO):
    raise NotImplementedError
