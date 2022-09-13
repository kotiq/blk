import pytest
from pytest import param as _, raises
from blk.types import LineComment, Name, Str


@pytest.mark.parametrize(['text', 'value'], [
    _('line comment', Str('line comment'), id='usual'),
    _('', Str(''), id='empty'),
])
def test_creat(text, value):
    n, v = LineComment(text)
    assert n == Name('@commentCPP')
    assert v == value


@pytest.mark.parametrize('text', [
    _('line\r\ncomment', id='windows'),
    _('line\ncomment', id='linux'),
])
def test_of_text_contains_newline_raises_ValueError(text):
    with raises(ValueError):
        LineComment.of(text)


@pytest.mark.parametrize(['value', 'text'], [
    _(LineComment('line comment'), "LineComment('line comment')", id='usual'),
    _(LineComment(''), "LineComment('')", id='empty'),
])
def test_repr(value, text):
    assert repr(value) == text
    assert eval(text) == value
