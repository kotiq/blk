"""dict dispatch, rec serialize"""

import re
from functools import partial
from typing import Iterable, TextIO, Tuple, Type, cast
from blk.format_ import dgen_float, dgen_float_element
from blk.types import (BlockComment, Bool, Color, Float, Float2, Float3, Float4, Float12, Include, Int, Int2, Int3,
                       Item, Section, Str, LineComment, Long, Vector)
from .dialect import DefaultDialect, DGEN, DQN, VQN, DQS, VQS, bool_map, float_map, int_map
from .constants import types_tags_map
from .error import SerializeError

__all__ = [
    'serialize',
]


def quoted_text(inst: str, quote: str) -> str:
    acc = [quote]
    for c in inst:
        if c in ('~', '"', "'"):
            acc.append('~')
            acc.append(c)
        elif c == '\t':
            acc.append('~t')
        elif c == '\n':
            acc.append('~n')
        elif c == '\r':
            acc.append('~r')
        else:
            acc.append(c)
    acc.append(quote)
    return ''.join(acc)


quoteless_name = re.compile(r"^[\w.\-]+$")
newline = re.compile(r'\r\n|\r|\n')


def dq_str_text(x: str) -> str:
    return quoted_text(x, '"')


dq_name_text = dq_str_text


def vq_str_text(x: str) -> str:
    dq = '"' in x
    sq = "'" in x
    if dq and sq:
        quote = '"'
    elif dq:
        quote = "'"
    else:
        quote = '"'
    return quoted_text(x, quote)


def vq_name_text(x: str) -> str:
    return x if quoteless_name.match(x) else quoted_text(x, '"')


def make_int_text(cls: Type):
    key = cls.__name__.lower()

    def text(self, value: int):
        return format(value, getattr(self, key))

    return text


def dgen_float_text(x: float) -> str:
    return repr(dgen_float(x))


def make_ints_text(cls: Type[Vector]):
    key = cls.type.__name__.lower()

    def text(self, value: Tuple[int, ...]) -> str:
        fmt = getattr(self, key)
        return ', '.join(map(lambda x: format(x, fmt), value))

    return text


def dgen_float_element_text(x: float) -> str:
    return repr(dgen_float_element(x))


def make_floats_text(cls: Type[Vector]):
    key = cls.type.__name__.lower()

    def text(self, value: Tuple[float, ...]) -> str:
        fmt = getattr(self, key)
        if fmt == DGEN:
            format_ = dgen_float_element_text
        else:
            def format_(x):
                return format(x, fmt)

        return ', '.join(map(format_, value))

    return text


def v_text(sep: str):
    def text(xs: Iterable) -> str:
        return f"[{sep.join(xs)}]"

    return text


r_text = v_text(', ')
m_text = v_text(' ')


class Serializer:
    def __init__(self, stream: TextIO,
                 dialect: Type[DefaultDialect],
                 check_cycle: bool = False,
                 ) -> None:
        self.stream = stream
        self.scale = dialect.scale
        self.eof_newline = dialect.eof_newline
        self.false, self.true = bool_map[dialect.bool_format]
        self.int = int_map[dialect.int_format]
        self.long = int_map[dialect.long_format]
        self.ubyte = int_map[dialect.ubyte_format]
        self.float = float_map[dialect.float_format]
        self.str = dialect.str_format
        self.name = dialect.name_format
        self.name_type_sep = dialect.name_type_sep
        self.type_value_sep = dialect.type_value_sep
        self.name_opener_sep = dialect.name_opener_sep
        self.sec_opener = dialect.sec_opener
        self.fst = ...
        self.level = 0
        self.check_cycle = check_cycle

        self.types_text_map = {
            Bool: self.bool_text,
            Str: self.str_text,
            Int: partial(make_int_text(Int), self),
            Long: partial(make_int_text(Long), self),
            Float: self.float_text,
            Int2: partial(make_ints_text(Int2), self),
            Int3: partial(make_ints_text(Int3), self),
            Color: partial(make_ints_text(Color), self),
            Float2: partial(make_floats_text(Float2), self),
            Float3: partial(make_floats_text(Float3), self),
            Float4: partial(make_floats_text(Float4), self),
            Float12: self.mat_text,
        }

    def indent(self) -> None:
        self.stream.write(' ' * self.scale * self.level)

    def serialize(self, root: Section, str_commands: bool = False) -> None:
        """
        Сериализация корневой секции.

        :param root: корневая секция
        :param str_commands: представить команды как строки
        :raises SectionError: ошибка структуры секции
        :raises SerializeError: ошибка ввода-вывода
        """

        if root:
            if self.check_cycle:
                root.check_cycle()
            self.fst = True
            try:
                self.serialize_pairs(root.pairs(), self.stream, str_commands)
            except OSError as e:
                raise SerializeError(e)
        if self.eof_newline:
            try:
                self.stream.write('\n')
            except OSError as e:
                raise SerializeError(e)

    def str_text(self, value: str) -> str:
        fmt = self.str
        if fmt == DQS:
            return dq_str_text(value)
        elif fmt == VQS:
            return vq_str_text(value)
        else:
            raise ValueError('Неизвестный формат: {}'.format(fmt))

    def name_text(self, value: str) -> str:
        fmt = self.name
        if fmt == DQN:
            return dq_name_text(value)
        elif fmt == VQN:
            return vq_name_text(value)
        else:
            raise ValueError('Неизвестный формат: {}'.format(fmt))

    def bool_text(self, value: bool) -> str:
        return self.true if value else self.false

    def float_text(self, value: float) -> str:
        fmt = self.float
        if fmt == DGEN:
            return dgen_float_text(value)
        else:
            return format(value, fmt)

    def mat_text(self, value: Tuple[float, ...]) -> str:
        fmt = self.float
        if fmt == DGEN:
            format_ = dgen_float_element_text
        else:
            def format_(x):
                return format(x, fmt)
        xs = map(format_, value)
        ts = zip(*[iter(xs)]*3)

        return m_text(map(r_text, ts))

    def serialize_pairs(self, pairs: Iterable[Item], stream: TextIO, str_commands: bool) -> None:
        for name, value in pairs:
            is_section = isinstance(value, Section)

            if self.fst:
                self.fst = False
            else:
                stream.write('\n')
                if is_section:
                    if self.sec_opener:
                        stream.write(self.sec_opener)

            self.indent()

            if isinstance(value, Str) and not str_commands:
                if name == Include.name:
                    stream.write(f'include {self.str_text(value)}')
                elif name == LineComment.name:
                    stream.write(f'// {value}')
                elif name == BlockComment.name:
                    stream.write('/*')
                    for line in newline.split(value):
                        stream.write('\n')
                        self.indent()
                        stream.write(line)
                    stream.write('\n')
                    self.indent()
                    stream.write('*/')
                else:
                    stream.write(self.name_text(name))
                    tag = types_tags_map[Str]
                    stream.write(f'{self.name_type_sep}{tag}{self.type_value_sep}{self.str_text(value)}')
            # иначе предупредить об Item со специальным именем
            else:
                stream.write(self.name_text(name))
                if is_section:
                    if self.name_opener_sep:
                        stream.write(self.name_opener_sep)
                    stream.write('{')
                    self.level += 1
                    self.serialize_pairs(cast(Section, value).pairs(), stream, str_commands)  # @r
                    self.level -= 1
                    stream.write('\n')
                    self.indent()
                    stream.write('}')
                else:
                    type_ = value.__class__
                    value_text = self.types_text_map[type_](value)
                    tag = types_tags_map[type_]
                    stream.write(f'{self.name_type_sep}{tag}{self.type_value_sep}{value_text}')


def serialize(root: Section, stream: TextIO,
              dialect: Type[DefaultDialect] = DefaultDialect,
              check_cycle: bool = False,
              str_commands: bool = False,
              ) -> None:
    """
    Сериализация корневой секции в текстовый поток.

    :param root: корневая секция
    :param stream: текстовый поток
    :param dialect: диалект, определяет детали представления
    :param check_cycle: проверить секцию на наличие циклов
    :param str_commands: представить команды как строки
    :raises SectionError: ошибка обработки секции
    :raises SerializeError: ошибка ввода-вывода
    """

    s = Serializer(stream, dialect, check_cycle)
    s.serialize(root, str_commands)
