import pytest
from blk.types import Long


@pytest.mark.parametrize(['sample', 'expected'], [
    pytest.param(0x1_0000_0000, 0x1_0000_0000, id='usual'),
    pytest.param(0x7fff_ffff_ffff_ffff, 0x7fff_ffff_ffff_ffff, id='max'),
    pytest.param(-0x8000_0000_0000_0000, -0x8000_0000_0000_0000, id='min'),
])
def test_of(sample, expected):
    assert Long.of(sample) == expected


@pytest.mark.parametrize('sample', [
    pytest.param(1.0, id='float'),
    pytest.param('1', id='str'),
])
def test_of_non_int_raises_type_error(sample):
    with pytest.raises(TypeError) as ei:
        Long.of(sample)
    print(ei.value)


@pytest.mark.parametrize('sample', [
    pytest.param(0x8000_0000_0000_0000, id='next max'),
    pytest.param(-0x8000_0000_0000_0001, id='prev min'),
])
def test_of_out_of_range_raises_value_error(sample):
    with pytest.raises(ValueError) as ei:
        Long.of(sample)
    print(ei.value)


@pytest.mark.parametrize(['value', 'text'], [
    pytest.param(Long(0x1_0000_0000), 'Long(4294967296)', id='usual')
])
def test_repr(value, text):
    assert repr(value) == text
    assert eval(text) == value
