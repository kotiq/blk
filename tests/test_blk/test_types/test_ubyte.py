import pytest
from pytest import param as _
from blk.types import UByte


@pytest.mark.parametrize(['sample', 'expected'], [
    _(18, 18, id='usual'),
    _(0xff, 0xff, id='max'),
    _(0, 0, id='min'),
])
def test_of(sample, expected):
    pass


@pytest.mark.parametrize('sample', [
    _(1.0, id='float'),
    _('1', id='str')
])
def test_of_non_int_raises_type_error(sample):
    with pytest.raises(TypeError) as ei:
        UByte.of(sample)
    print(ei.value)


@pytest.mark.parametrize('sample', [
    _(0x100, id='next max'),
    _(-1, id='prev min'),
])
def test_put_of_range_raises_value_error(sample):
    with pytest.raises(ValueError) as ei:
        UByte.of(sample)
    print(ei.value)


@pytest.mark.parametrize(['value', 'text'], [
    _(UByte(0x12), 'UByte(18)', id='usual')
])
def test_repr(value, text):
    assert repr(value) == text
    assert eval(text) == value
