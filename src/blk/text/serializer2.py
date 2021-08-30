"""cls dispatch, iter items gen"""

import re
from blk.types import *
from .dialect import *

__all__ = ['serialize', 'serialize_items']

for cls, tag in types_tags_map.items():
    cls.tag = tag


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


class Serializer:
    def __init__(self, stream, dialect):
        self.stream = stream
        self.scale = dialect.scale
        self.eof_newline = dialect.eof_newline

        self.context = {}
        self.context.update(zip(('false', 'true'), bool_map[dialect.bool_format]))
        self.context.update({
            'name': dialect.name_format,
            'str': dialect.str_format,
            'int': int_map[dialect.int_format],
            'long': int_map[dialect.long_format],
            'ubyte': int_map[dialect.ubyte_format],
            'float': float_map[dialect.float_format]
        })
        self.context['name_type_sep'] = dialect.name_type_sep
        self.context['type_value_sep'] = dialect.type_value_sep
        self.context['name_opener_sep'] = dialect.name_opener_sep
        self.context['sec_opener'] = dialect.sec_opener

    def indent(self, level):
        self.stream.write(' ' * self.scale * level)

    def serialize(self, root: Section):
        if root:
            self.context['fst'] = True
            serialize_items(root.dfs_nlr_items(), self.stream, self.indent, 0, self.context)
        if self.eof_newline:
            self.stream.write('\n')


def serialize_items(items, stream, indent, level, context):
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
            if context['fst']:
                context['fst'] = False
            else:
                stream.write('\n')
                if is_section:
                    sec_opener = context['sec_opener']
                    if sec_opener:
                        stream.write(sec_opener)

            indent(level)
            name.serialize_text(stream, context)
            if is_section:
                name_opener_sep = context['name_opener_sep']
                if name_opener_sep:
                    stream.write(name_opener_sep)
                stream.write('{')
                sections += 1
                level += 1
            else:
                value.serialize_text(stream, context)


@method(Name)
def serialize_text(self, stream, context):
    fmt = context['name']
    if fmt == DQN:
        txt = dq_name_text(self)
    elif fmt == VQN:
        txt = vq_name_text(self)
    else:
        raise ValueError('Неизвестный формат: {}'.format(fmt))

    stream.write(txt)


@method(Parameter)
def serialize_text(self, stream, context):
    name_type_sep = context['name_type_sep']
    type_value_sep = context['type_value_sep']
    stream.write(f'{name_type_sep}{self.tag}{type_value_sep}{self.text(context)}')


def serialize(root, stream, dialect=DefaultDialect):
    s = Serializer(stream, dialect)
    s.serialize(root)


@method(Str)
def text(self, context):
    fmt = context['str']
    if fmt == DQS:
        return dq_str_text(self)
    elif fmt == VQS:
        return vq_str_text(self)
    else:
        raise ValueError('Неизвестный формат: {}'.format(fmt))


@method(Bool)
def text(self, context):
    return context['true'] if self else context['false']


def register_int_text(cls):
    key = cls.__name__.lower()

    @method(cls)
    def text(self, context):
        return format(self, context[key])


for cls in Int, Long:
    register_int_text(cls)


def dgen_float_text(x):
    return repr(round(x, 4))


@method(Float)
def text(self, context):
    fmt = context['float']
    if fmt == DGEN:
        return dgen_float_text(self)
    else:
        return format(self, fmt)


def register_ints_text(cls):
    key = cls.type.__name__.lower()

    @method(cls)
    def text(self, context):
        fmt = context[key]
        return ', '.join(map(lambda x: format(x, fmt), self))


for cls in Int2, Int3, Color:
    register_ints_text(cls)


def dgen_floats_text(x):
    return repr(float(format(x, 'e')))


def register_floats_text(cls):
    key = cls.type.__name__.lower()

    @method(cls)
    def text(self, context):
        fmt = context[key]
        if fmt == DGEN:
            format_ = dgen_floats_text
        else:
            def format_(x):
                return format(x, fmt)

        return ', '.join(map(format_, self))


for cls in Float2, Float3, Float4:
    register_floats_text(cls)


def v_text(sep):
    return lambda xs: f"[{sep.join(xs)}]"


r_text = v_text(', ')
m_text = v_text(' ')


@method(Float12)
def text(self, context):
    fmt = context['float']
    if fmt == DGEN:
        format_ = dgen_floats_text
    else:
        def format_(x):
            return format(x, fmt)
    xs = map(format_, self)
    ts = zip(*[iter(xs)]*3)

    return m_text(map(r_text, ts))
