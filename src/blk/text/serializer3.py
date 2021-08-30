"""dict dispatch, rec items gen"""

import re
from functools import partial
from blk.types import *
from .dialect import *

__all__ = ['serialize']


def quoted_text(inst, quote):
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


def dq_str_text(x):
    return quoted_text(x, '"')


dq_name_text = dq_str_text


def vq_str_text(x):
    dq = '"' in x
    sq = "'" in x
    if dq and sq:
        quote = '"'
    elif dq:
        quote = "'"
    else:
        quote = '"'
    return quoted_text(x, quote)


def vq_name_text(x):
    return x if quoteless_name.match(x) else quoted_text(x, '"')


def make_int_text(cls):
    key = cls.__name__.lower()

    def text(self, value):
        return format(value, getattr(self, key))

    return text


def dgen_float_text(x):
    return repr(round(x, 4))


def make_ints_text(cls):
    key = cls.type.__name__.lower()

    def text(self, value):
        fmt = getattr(self, key)
        return ', '.join(map(lambda x: format(x, fmt), value))

    return text


def dgen_floats_text(x):
    return repr(float(format(x, 'e')))


def make_floats_text(cls):
    key = cls.type.__name__.lower()

    def text(self, value):
        fmt = getattr(self, key)
        if fmt == DGEN:
            format_ = dgen_floats_text
        else:
            def format_(x):
                return format(x, fmt)

        return ', '.join(map(format_, value))

    return text


def v_text(sep):
    def text(xs):
        return f"[{sep.join(xs)}]"

    return text


r_text = v_text(', ')
m_text = v_text(' ')


class Serializer:
    def __init__(self, stream, dialect):
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

    def indent(self, level):
        self.stream.write(' ' * self.scale * level)

    def serialize(self, root: Section):
        if root:
            self.fst = True
            self.serialize_items(root.dfs_nlr_items_rec(), self.stream, self.indent, 0)
        if self.eof_newline:
            self.stream.write('\n')

    def str_text(self, value):
        fmt = self.str
        if fmt == DQS:
            return dq_str_text(value)
        elif fmt == VQS:
            return vq_str_text(value)
        else:
            raise ValueError('Неизвестный формат: {}'.format(fmt))

    def name_text(self, value):
        fmt = self.name
        if fmt == DQN:
            return dq_name_text(value)
        elif fmt == VQN:
            return vq_name_text(value)
        else:
            raise ValueError('Неизвестный формат: {}'.format(fmt))

    def bool_text(self, value):
        return self.true if value else self.false

    def float_text(self, value):
        fmt = self.float
        if fmt == DGEN:
            return dgen_float_text(value)
        else:
            return format(value, fmt)

    def mat_text(self, value):
        fmt = self.float
        if fmt == DGEN:
            format_ = dgen_floats_text
        else:
            def format_(x):
                return format(x, fmt)
        xs = map(format_, value)
        ts = zip(*[iter(xs)]*3)

        return m_text(map(r_text, ts))

    def serialize_items(self, items, stream, indent, level):
        sections = 0
        next(items)  # skip root header
        for item in items:
            if item is Section.end:
                if sections > 0:
                    level -= 1
                    stream.write('\n')
                    indent(level)
                    stream.write('}')
                    sections -= 1
                else:
                    return  # skip root footer
            else:
                name, value = item
                is_section = isinstance(value, Section)
                if self.fst:
                    self.fst = False
                else:
                    stream.write('\n')
                    if is_section:
                        if self.sec_opener:
                            stream.write(self.sec_opener)

                indent(level)
                stream.write(self.name_text(name))
                if is_section:
                    if self.name_opener_sep:
                        stream.write(self.name_opener_sep)
                    stream.write('{')
                    sections += 1
                    level += 1
                else:
                    type_ = value.__class__
                    value_text = self.types_text_map[type_](value)
                    tag = types_tags_map[type_]
                    stream.write(f'{self.name_type_sep}{tag}{self.type_value_sep}{value_text}')


def serialize(root, stream, dialect=DefaultDialect):
    s = Serializer(stream, dialect)
    s.serialize(root)
