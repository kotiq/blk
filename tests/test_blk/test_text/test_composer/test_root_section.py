from pytest import mark, raises, param as _
from pytest_lazyfixture import lazy_fixture as lf
import parsy as ps
from blk.types import ListSection
from blk.text.composer import root_section


@mark.parametrize(['text', 'value'], [
    _('', lf('empty'), id='empty'),
    _('"int":i = 42', lf('section_oneline_param'), id='oneline param'),
    _('"int":i = 42  // integer', lf('section_oneline_param_with_line_comment'), id='oneline param with comment'),
])
def test_compose_section(text, value):
    parsed = root_section.parse(text)
    assert isinstance(parsed, ListSection)
    assert parsed == value


@mark.xfail(reason='Упрощенная грамматика')
@mark.parametrize('text', [
    _('"x":i = 1/*comment*/"y":i = 2', id='null'),
    _('"x":i = 1 "y":i = 2', id='space')
])
def test_compose_root_section_named_params_separator_raises_parse_error(text):
    with raises(ps.ParseError):
        root_section.parse(text)
