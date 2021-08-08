import re
from ..types import *

__all__ = ['serialize', 'serialize_pair', 'serialize_pairs', 'DefaultDialect', 'StrictDialect']


EXP = 'exp'
GEN = 'gen'
DGEN = 'dgen'
dgen_fmt = object()

LOG = 'log'
ANS = 'ans'
SW = 'sw'
ALG = 'alg'

HEX = '#x'
DEC = 'd'

bool_map = {
    LOG: ('false', 'true'),
    ANS: ('no', 'yes'),
    SW: ('off', 'on'),
    ALG: ('0', '1'),
}

float_map = {
    EXP: '.7e',
    GEN: '.7g',
    DGEN: dgen_fmt,
}

int_map = {
    HEX: '#x',
    DEC: 'd',
}


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


class DefaultDialect:
    scale = 2
    float_format = GEN
    bool_format = LOG
    ubyte_format = HEX
    long_format = HEX
    int_format = DEC
    name_type_sep = ':'
    type_value_sep = ' = '
    name_opener_sep = ' '
    sec_opener = ''

    def str_text(inst):
        return quoted_text(inst, '"')

    name_text = str_text


class StrictDialect(DefaultDialect):
    bool_format = ANS
    float_format = DGEN
    ubyte_format = DEC
    long_format = DEC
    type_value_sep = '='
    name_opener_sep = ''
    sec_opener = '\n'

    def name_text(inst):
        return inst if quoteless_name.match(inst) else quoted_text(inst, '"')

    def str_text(inst):
        dq = '"' in inst
        sq = "'" in inst
        if dq and sq:
            quote = '"'
        elif dq:
            quote = "'"
        else:
            quote = '"'
        return quoted_text(inst, quote)


class Serializer:
    def __init__(self, stream, dialect):
        self.stream = stream
        self.scale = dialect.scale

        self.context = {}
        self.context.update(zip(('false', 'true'), bool_map[dialect.bool_format]))
        self.context.update({
            'int': int_map[dialect.int_format],
            'long': int_map[dialect.long_format],
            'ubyte': int_map[dialect.ubyte_format],
            'float': float_map[dialect.float_format]
        })
        self.context['name_type_sep'] = dialect.name_type_sep
        self.context['type_value_sep'] = dialect.type_value_sep
        self.context['name_opener_sep'] = dialect.name_opener_sep
        self.context['sec_opener'] = dialect.sec_opener

        self.context['str_text'] = dialect.str_text
        self.context['name_text'] = dialect.name_text

    def indent(self, level):
        self.stream.write(' ' * self.scale * level)

    def serialize(self, root):
        # первое и последнее значения для пропуска sec_opener вначале и разделителя пар в конце
        if root:
            self.context['fst'] = True
            serialize_pairs(root.pairs(), self.stream, self.indent, 0, self.context)


@method(Section)
def serialize_text(self, stream, indent, level, context):
    name_opener_sep = context['name_opener_sep']
    stream.write(f'{name_opener_sep}{{')
    level += 1
    serialize_pairs(self.pairs(), stream, indent, level, context)
    level -= 1
    stream.write('\n')
    indent(level)
    stream.write('}')


def serialize_pair(name, value, stream, indent, level, context):
    if context['fst']:
        context['fst'] = False
    else:
        if isinstance(value, Section):
            if sec_opener := context['sec_opener']:
                stream.write(sec_opener)
        stream.write('\n')

    indent(level)
    name.serialize_text(stream, context)
    value.serialize_text(stream, indent, level, context)


def serialize_pairs(pairs, stream, indent, level, context):
    for n, v in pairs:
        serialize_pair(n, v, stream, indent, level, context)


@method(Name)
def serialize_text(self, stream, context):
    name_text = context['name_text']
    stream.write(name_text(self))


@method(Parameter)
def serialize_text(self, stream, indent, level, context):
    name_type_sep = context['name_type_sep']
    type_value_sep = context['type_value_sep']
    stream.write(f'{name_type_sep}{self.tag}{type_value_sep}{self.text(context)}')


def serialize(root, stream, dialect=DefaultDialect):
    s = Serializer(stream, dialect)
    s.serialize(root)


@method(Str)
def text(self, context):
    str_text = context['str_text']
    return str_text(self)


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


@method(Float)
def text(self, context):
    fmt = context['float']
    if fmt == dgen_fmt:
        x = round(self, 4)
        return floatstr(x)
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


def register_floats_text(cls):
    key = cls.type.__name__.lower()

    @method(cls)
    def text(self, context):
        fmt = context[key]
        if fmt == dgen_fmt:
            format_ = floatstr
        else:
            format_ = lambda x: format(x, fmt)

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
    if fmt == dgen_fmt:
        format_ = floatstr
    else:
        format_ = lambda x: format(x, fmt)
    xs = map(format_, self)
    ts = zip(*[iter(xs)]*3)

    return m_text(map(r_text, ts))
