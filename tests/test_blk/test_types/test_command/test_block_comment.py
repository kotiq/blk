import pytest
from pytest import param as _
from blk.types import BlockComment, Name, Str


@pytest.mark.parametrize(['text', 'value'], [
    _('block\ncomment', Str('block\ncomment'), id='usual'),
    _('', Str(''), id='empty')
])
def test_creat(text, value):
    n, v = BlockComment(text)
    assert n == Name('@commentC')
    assert v == value


@pytest.mark.parametrize('text', [
    _('/*inner block comment*/', id='inner'),
    _('"rpn":t = "6 2 3 */"', id='string'),
])
def test_of_text_contains_star_slash_raises_ValueError(text):
    with pytest.raises(ValueError):
        BlockComment.of(text)


@pytest.mark.parametrize(['value', 'text'], [
    _(BlockComment('block\ncomment'), r"BlockComment('block\ncomment')", id='usual'),
    _(BlockComment(''), "BlockComment('')", id='empty'),
])
def test_repr(value, text):
    assert repr(value) == text
    assert eval(text) == value
