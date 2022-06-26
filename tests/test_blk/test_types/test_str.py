import pytest
from pytest import param as _
from blk.types import Str


@pytest.mark.parametrize(['sample', 'expected'], [
    _('', '', id='empty'),
    _('hello', 'hello', id='ascii text'),
    _('привет', 'привет', id='utf8 text'),
    _(b'hello', 'hello', id='ascii bytes'),
    _('привет'.encode('utf8'), 'привет', id='utf8 bytes'),
    _('привет'.encode('cp1251'), 'привет', id='cp1251 bytes'),
])
def test_of(sample, expected):
    assert Str.of(sample) == expected


@pytest.mark.parametrize('sample', [
    _(1, id='int'),
    _(1.0, id='float'),
])
def test_of_non_anystr_raises_type_error(sample):
    with pytest.raises(TypeError) as ei:
        Str.of(sample)
    print(ei.value)


@pytest.mark.parametrize('sample', [
    _(b'\x98', id='0x98 undefined')
])
def test_of_unknown_encoding_raises_value_error(sample):
    with pytest.raises(ValueError) as ei:
        Str.of(sample)
    print(ei.value)


def test_repr():
    assert repr(Str('Hello')) == "Str('Hello')"
