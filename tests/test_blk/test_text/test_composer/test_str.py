import pytest
from pytest import param as _
from blk.types import Str
from blk.text.composer import double_single_quoted_str, string, triple_quoted_str, unquoted_str


@pytest.mark.parametrize(['text', 'value'], [
    _('hello_world', Str('hello_world'),  id='unquoted'),
])
def test_compose_uq_str(text, value):
    parsed = unquoted_str.parse(text)
    assert isinstance(parsed, Str)
    assert parsed == value


@pytest.mark.parametrize(['text', 'value'], [
    _("'hello \"world\"'", Str('hello "world"'), id='single quoted'),
    _('"hello \'world\'"', Str("hello 'world'"), id='double quoted'),
    _('"hello ~"~w~o~r~l~d~""', Str('hello "wo\rld"'), id='escaped double quoted')

])
def test_compose_sq_dq_str(text, value):
    parsed = double_single_quoted_str.parse(text)
    assert isinstance(parsed, Str)
    assert parsed == value


multiline_triple_double_quoted = """\"\"\"
hello
world
\"\"\""""


@pytest.mark.parametrize(['text', 'value'], [
    _("'''hello \"world\"'''", Str('hello "world"'), id='triple single quoted'),
    _("'''hello~tworld'''", Str('hello\tworld'), id='escaped single quoted'),
    _("'''hello ~\'\'\' world'''", Str("hello ''' world"), id='triple single quoted with escaped sentinel'),
    _('"""hello \'world\'"""',  Str("hello 'world'"), id='triple double quoted'),
    _(multiline_triple_double_quoted, Str('\nhello\nworld\n'), id='multiline triple double quoted'),
])
def test_compose_tq_sq_dq_str(text, value):
    parsed = triple_quoted_str.parse(text)
    assert isinstance(parsed, Str)
    assert parsed == value


@pytest.mark.parametrize(['text', 'value'], [
    _('hello', Str('hello'), id='unquoted'),
    _('"hello world"', Str('hello world'), id='double quoted'),
    _('"""hello world"""', Str('hello world'), id='triple double quoted'),
])
def test_compose_string(text, value):
    parsed = string.parse(text)
    assert isinstance(parsed, Str)
    assert parsed == value
