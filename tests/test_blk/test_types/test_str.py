import pytest
from blk.types import Str


@pytest.mark.parametrize(['sample', 'expected'], [
    pytest.param('', '', id='empty'),
    pytest.param('hello', 'hello', id='ascii text'),
    pytest.param('привет', 'привет', id='utf8 text'),
    pytest.param(b'hello', 'hello', id='ascii bytes'),
    pytest.param('привет'.encode('utf8'), 'привет', id='utf8 bytes'),
    pytest.param('привет'.encode('cp1251'), 'привет', id='cp1251 bytes'),
])
def test_of(sample, expected):
    assert Str.of(sample) == expected


@pytest.mark.parametrize('sample', [
    pytest.param(1, id='int'),
    pytest.param(1.0, id='float'),
])
def test_of_non_anystr_raises_type_error(sample):
    with pytest.raises(TypeError) as ei:
        Str.of(sample)
    print(ei.value)


@pytest.mark.parametrize('sample', [
    pytest.param(b'\x98', id='0x98 undefined')
])
def test_of_unknown_encoding_raises_value_error(sample):
    with pytest.raises(ValueError) as ei:
        Str.of(sample)
    print(ei.value)


def test_repr():
    assert repr(Str('Hello')) == "Str('Hello')"
