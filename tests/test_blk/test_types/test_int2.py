import pytest
from blk.types import Int2


@pytest.mark.parametrize(['sample', 'expected'], [
    pytest.param((512, 1024), Int2((512, 1024)), id='usual'),
    pytest.param((-0x8000_0000, 1), Int2((-0x8000_0000, 1)), id='min'),
    pytest.param((1, 0x7fff_ffff), Int2((1, 0x7fff_ffff)), id='max'),
])
def test_of(sample, expected):
    assert Int2.of(sample) == expected


@pytest.mark.parametrize('sample', [
    pytest.param((1.0, 1), id='float'),
    pytest.param(('1', 1), id='str'),
])
def test_of_non_ints_raises_type_error(sample):
    with pytest.raises(TypeError) as ei:
        Int2.of(sample)
    print(ei.value)


@pytest.mark.parametrize('sample', [
    pytest.param((1, ), id='less'),
    pytest.param((1, 2, 3), id='great'),
])
def test_of_wrong_init_size_raises_type_error(sample):
    with pytest.raises(TypeError) as ei:
        Int2.of(sample)
    print(ei.value)


@pytest.mark.parametrize('sample', [
    pytest.param((-0x8000_0001, 1), id='prev min'),
    pytest.param((1, 0x8000_0000), id='next_max'),
])
def test_of_out_of_range_raises_value_error(sample):
    with pytest.raises(ValueError) as ei:
        Int2.of(sample)
    print(ei.value)


@pytest.mark.parametrize(['value', 'text'], [
    pytest.param(Int2((512, 1024)), 'Int2((512, 1024))', id='usual')
])
def test_repr(value, text):
    assert repr(value) == text
    assert eval(text) == value
