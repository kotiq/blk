import pytest
from blk.types import UByte


@pytest.mark.parametrize(['sample', 'expected'], [
    pytest.param(18, 18, id='usual'),
    pytest.param(0xff, 0xff, id='max'),
    pytest.param(0, 0, id='min'),
])
def test_of(sample, expected):
    pass


@pytest.mark.parametrize('sample', [
    pytest.param(1.0, id='float'),
    pytest.param('1', id='str')
])
def test_of_non_int_raises_type_error(sample):
    with pytest.raises(TypeError) as ei:
        UByte.of(sample)
    print(ei.value)


@pytest.mark.parametrize('sample', [
    pytest.param(0x100, id='next max'),
    pytest.param(-1, id='prev min'),
])
def test_put_of_range_raises_value_error(sample):
    with pytest.raises(ValueError) as ei:
        UByte.of(sample)
    print(ei.value)


@pytest.mark.parametrize(['value', 'text'], [
    pytest.param(UByte(0x12), 'UByte(18)', id='usual')
])
def test_repr(value, text):
    assert repr(value) == text
    assert eval(text) == value
