from pytest import mark, param as _
from blk.types import false, true


def test_bool():
    assert true
    assert not false


@mark.parametrize(['value', 'text'], [
    _(false, 'false', id='false'),
    _(true, 'true', id='true'),
])
def test_repr(value, text):
    assert repr(value) == text
    assert eval(text) is value
