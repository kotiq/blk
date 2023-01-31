from itertools import chain
from pathlib import Path, PureWindowsPath
from re import ASCII, DOTALL
from typing import Callable, Optional, TextIO
import parsy as ps
from blk.types import (BlockComment, Bool, Color, Float, Float2, Float3, Float4, Float12, Include, SectionError,
                       Int, Int2, Int3, LineComment, ListSection, Long, Name, Parameter, Str, UByte, Value, false, true)
from .constants import types_tags_map
from .error import ComposeError

__all__ = [
    'compose',
    'compose_file',
]

quote = ps.char_from('"\'').desc('quote')

escaped = (ps.string('~') >> (
        ps.string('~') |
        ps.string("'") |
        ps.string('"') |
        ps.string('t').result('\t') |
        ps.string('n').result('\n') |
        ps.string('r').result('\r') |
        ps.regex('[^\t\n\r]')
)).desc('escaped char')


@ps.generate('single or double quoted or unquoted string')
def double_single_quoted_str() -> Str:
    """
    Строка в <'> или <"> кавычках или строка без кавычек.
    В строках с кавычками строго экранированы символы [~\t\r\n].
    В строках в <'> кавычках допустимы неэкранированные <"> кавычки.
    В строках в <"> кавычках допустимы неэкранированные <'> кавычки.
    В строках без кавычек недопустимы пробельные символы, кавычки и разделитель <;>.
    """

    quote_ = yield quote
    char = escaped | ps.regex(f'[^{quote_}~\t\n\r]')
    text = yield char.many().concat()
    yield ps.string(quote_)

    return Str(text)


unquoted_str = ps.regex(r'[^\s~\'";/]').many().concat().map(Str).desc('unquoted string')


@ps.generate('triple single or double quoted string')
def triple_quoted_str() -> Str:
    """
    Строка в тройных <'> или <"> кавычках для многострочных литералов.
    Пробельные символы как есть, так и экранированные [~\\\\t\\\\r\\\\n].
    """

    quotes = yield ps.regex(r'\'{3}|"{3}')
    raw_text = yield ps.regex(f'(?P<text>(~{quotes}|.)*?){quotes}', flags=DOTALL, group='text')
    char = escaped | ps.any_char
    text = char.many().concat().parse(raw_text)

    return Str(text)


string = triple_quoted_str | double_single_quoted_str | unquoted_str
"""Строка в тройных кавычках, строка в одинарных кавычках или строка без кавычек."""

boolean = (ps.string_from('true', 'yes', 'on', '1').result(true) |
           ps.string_from('false', 'no', 'off', '0').result(false)).desc('boolean')
"""Булево значение."""


def make_int_parser(parser: ps.Parser, ctor: Callable) -> ps.Parser:
    @ps.generate
    def int_parser():
        text = yield parser
        base = 16 if text[:2].lower() == '0x' else 10
        try:
            x = int(text, base)
        except ValueError as err:
            return ps.fail(str(err))
        return ctor(x)

    return int_parser


def make_float_parser(parser: ps.Parser) -> ps.Parser:
    @ps.generate
    def float_parser():
        text = yield parser
        try:
            x = float(text)
        except ValueError as err:
            return ps.fail(str(err))
        return Float.of(x)

    return float_parser


element = ps.regex('[^ \t,]+')
"""Элемент, кроме последнего."""

last_element = ps.regex('[^ \t\n;/]+')
"""Последний элемент или одиночное значение."""

ubyte_element = make_int_parser(element, UByte.of)
ubyte = ubyte_last_element = make_int_parser(last_element, UByte.of)

int_element = make_int_parser(element, Int.of)
integer = int_last_element = make_int_parser(last_element, Int.of)

long = make_int_parser(last_element, Long.of)

float_element = make_float_parser(element)
floating = float_last_element = make_float_parser(last_element)

line_comment = ps.regex(r'//([^\r\n]*)', group=1).map(str.lstrip).map(LineComment)
block_comment = ps.regex(r'/\*(.*?)\*/', DOTALL, 1).map(str.strip).map(BlockComment)
comment = line_comment | block_comment


@ps.generate('include')
def include() -> Include:
    p = yield ps.regex('include[ \t\n]+') >> string
    if not p:
        return ps.fail('Пустой путь.')
    if (
            p[0] in (Include.cdk_prefix, Include.root_prefix) and
            p[1] not in ('\\', '/')
    ):
        p = f'{p[0]}/{p[1:]}'
    path = PureWindowsPath(p).as_posix()
    return Include(str(path))


@ps.generate('name')
def name() -> Name:
    """
    Пусть символы в именах ограничены ASCII
    B именах в <"> не допускаются <">
    В именах в <'> не допускаются ['"]
    В именах без кавычек не допускаются [:{}'"\\\\s]
    """

    quote_ = yield quote.optional()

    if quote_ == '"':
        char = ps.regex(r'[^"]', ASCII).desc('double quoted name char')
    elif quote_ == "'":
        char = ps.regex(r'[^\'"]', ASCII).desc('single quoted name char')
    else:
        char = ps.regex(r'[^:{}\'"\s/]').desc('not quoted name char')

    text = yield char.at_least(1).concat()

    if quote_ is not None:
        yield ps.string(quote_)

    return Name(text)


def vector(e: ps.Parser, le: ps.Parser, s: ps.Parser, sz: int) -> ps.Parser:
    return ps.seq(*(e << s,) * (sz - 1), le)


value_sep = ps.regex('[ \t]*')
vector_element_sep = (value_sep >> ps.string(',') << value_sep).desc('vector element sep')


@ps.generate('color')
def color() -> Color:
    """
    Цвет RGBA.
    Если кортеж трехкомпонентный, A=255.
    """

    xs = yield (vector(ubyte_element, ubyte_last_element, vector_element_sep, Color.size)
                | vector(ubyte_element, ubyte_last_element, vector_element_sep, Color.size - 1))
    if len(xs) == Color.size - 1:
        xs.append(0xff)

    return Color(xs)


int2 = vector(int_element, int_last_element, vector_element_sep, Int2.size).map(Int2).desc('int2')
int3 = vector(int_element, int_last_element, vector_element_sep, Int3.size).map(Int3).desc('int3')

float2 = vector(float_element, float_last_element, vector_element_sep, Float2.size).map(Float2).desc('float2')
float3 = vector(float_element, float_last_element, vector_element_sep, Float3.size).map(Float3).desc('float3')
float4 = vector(float_element, float_last_element, vector_element_sep, Float4.size).map(Float4).desc('float4')

matrix_begin = ps.regex(r'(?:\[[ \t]*){2}').desc('begin matrix')
matrix_end = ps.regex(r'(?:[ \t]*]){2}').desc('end matrix')
matrix_vector_sep = ps.regex(r'[ \t]*][ \t]*\[[ \t]*').desc('matrix vector sep')

matrix_vector_last_element = make_float_parser(ps.regex(r'[^ \t\]]+')).desc('matrix vector last element')
float12 = (matrix_begin
           >> vector(float_element, matrix_vector_last_element, vector_element_sep, 3).sep_by(matrix_vector_sep, min=4, max=4).map(chain.from_iterable)
           << matrix_end).map(Float12).desc('float12')

sep = ps.regex('[ \t\n]*').desc('sep')
tag = ps.string_from(*types_tags_map.values()).desc('tag')
name_tag_sep = (sep >> ps.string(':') << sep << comment.optional() << sep).desc('*colon*')
tag_value_sep = (sep >> comment.optional() >> sep >> 
                 ps.string('=')
                 << sep << comment.optional() << sep).desc('*equal*')

types_parsers_map = {
    Int: integer,
    Long: long,
    Float: floating,
    Bool: boolean,
    Str: string,
    Float2: float2,
    Float3: float3,
    Float4: float4,
    Int2: int2,
    Int3: int3,
    Color: color,
    Float12: float12,
}

tags_parsers_map = {types_tags_map[t]: types_parsers_map[t] for t in types_tags_map}


@ps.generate('parameter value')
def parameter() -> Value:
    yield name_tag_sep
    t = yield tag
    yield tag_value_sep
    parser = tags_parsers_map[t]
    val = yield parser
    return val


item_sep = ps.regex('[ \t\n;]*').desc('item sep')
section_begin = (sep >> ps.string('{') << item_sep).desc('*{*')
section_end = item_sep >> ps.string('}').desc('*}')


@ps.generate('section value')
def section():
    yield section_begin
    val = yield items
    yield section_end
    return val


value = (parameter | section).desc('value')
named_value = ps.seq(name << sep << comment.optional(), value)
item = (comment | named_value | include).desc('item')


@ps.generate('items param sep name')
def items_param_sep_name() -> ListSection:
    sec = ListSection()
    after_named_param = False
    ss = []

    it = yield item.optional()
    if it is None:
        return sec

    if isinstance(it[1], Parameter):
        after_named_param = True

    sec.append(tuple(it))

    while True:
        s = yield item_sep
        it = yield item.optional()
        if it is None:
            break

        if isinstance(it, BlockComment):
            if after_named_param:
                if s:
                    ss.append(s)
        elif not isinstance(it, LineComment):
            is_param = isinstance(it[1], Parameter)
            is_section = isinstance(it[1], ListSection)
            if is_param or is_section:
                if s:
                    ss.append(s)
                if after_named_param:
                    if all(not ('\n' in s or ';' in s) for s in ss):
                        return ps.fail('Ожидался разделитель \\n|;')
                    ss.clear()
            if is_param:
                after_named_param = True
            elif is_section:
                after_named_param = False

        sec.append(tuple(it))

    return sec


@ps.generate('items')
def items() -> ListSection:
    sec = ListSection()
    its = yield item.sep_by(item_sep).map(lambda xs: map(tuple, xs))
    sec.extend(its)
    return sec


root_section = (item_sep >> items << item_sep).desc('root section')


def compose(stream: TextIO,
            remove_comments: bool = True,
            include_files: bool = True,
            working_path: Path = Path.cwd(),
            cdk_path: Optional[Path] = None,
            root_path: Optional[Path] = None,
            ) -> ListSection:
    try:
        content = stream.read()
        sec: ListSection = root_section.parse(content)
        if include_files:
            sec.include_files(working_path, cdk_path, root_path)
        if remove_comments:
            sec.remove_comments()
        return sec
    except (OSError, ps.ParseError, SectionError) as e:
        raise ComposeError(e)


def compose_file(path: Path,
                 remove_comments: bool = True,
                 include_files: bool = True,
                 cdk_path: Optional[Path] = None,
                 root_path: Optional[Path] = None,
                 ) -> ListSection:
    working_path = path.parent
    with open(path) as stream:  # raises OSError
        return compose(stream, remove_comments, include_files, working_path, cdk_path, root_path)  # raises ComposeError
