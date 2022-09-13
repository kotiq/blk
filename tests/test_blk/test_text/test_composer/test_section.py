from pytest import mark, raises, param as _
import parsy as ps
from blk.types import Int, ListSection, Name, Str
from blk.text.composer import root_section


@mark.parametrize(['text', 'value'], [
    _('', ListSection(), id='empty'),
    _('"int":i = 42', ListSection([(Name('int'), Int(42))]), id='oneline param'),
    _('"int":i = 42  // integer', ListSection([(Name('int'), Int(42)), (Name('@commentCPP'), Str('integer'))]), id='oneline param with comment'),
])
def test_section(text, value):
    parsed = root_section.parse(text)
    assert isinstance(parsed, ListSection)
    assert parsed == value


@mark.xfail(reason='Упрощенная грамматика')
@mark.parametrize('text', [
    _('"x":i = 1/*comment*/"y":i = 2', id='null'),
    _('"x":i = 1 "y":i = 2', id='space')
])
def test_named_params_separator_raises_parse_error(text):
    with raises(ps.ParseError):
        root_section.parse(text)
