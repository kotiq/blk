from pytest import mark, param as _
from pytest_lazyfixture import lazy_fixture as lf
from blk.types import ListSection
from blk.text.composer import section

@mark.parametrize(['text', 'value'], [
    _('{\nint:i=42\n}', lf('section_oneline_param'), id='oneline param newline items sep'),
    _('{int:i=42}', lf('section_oneline_param'), id='oneline param compact'),
    _('{int:i=42;}', lf('section_oneline_param'), id='oneline param compact semicolon line terminator'),
    _('{int:i=42//integer\n}', lf('section_oneline_param_with_line_comment'), id='oneline param compact with comment no space'),
])
def test_compose_section(text, value):
    parsed = section.parse(text)
    assert isinstance(parsed, ListSection)
    assert parsed == value
