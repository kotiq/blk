import pytest
from blk.types import Float2
from .test_float import approx


@pytest.mark.parametrize(['sample', 'expected'], [
    pytest.param((123.456, 789.012), Float2((123.456, 789.012)),  id='usual'),
    pytest.param((3.4028235e+38, 1.0), Float2((3.4028235e+38, 1.0)), id='max'),
    pytest.param((1.0, -3.4028235e+38), Float2((1.0, -3.4028235e+38)), id='min'),
    pytest.param((1.1754944e-38, 1.0), Float2((1.1754944e-38, 1.0)), id='tiny'),
])
def test_of(sample, expected):
    assert all(x == approx(y) for x, y in zip(Float2.of(sample), expected))


@pytest.mark.parametrize('sample', [
    pytest.param(('1.0', 1.0), id='str'),
])
def test_of_non_numbers_raises_type_error(sample):
    with pytest.raises(TypeError) as ei:
        Float2.of(sample)
    print(ei.value)


@pytest.mark.parametrize('sample', [
    pytest.param((1.0, ), id='less'),
    pytest.param((1.0, 2.0, 3.0), id='great'),
])
def test_of_wrong_init_size_raises_type_error(sample):
    with pytest.raises(TypeError) as ei:
        Float2.of(sample)
    print(ei.value)


@pytest.mark.parametrize(['xs', 'ys'], [
    pytest.param(Float2((0.0, 0.0)), (1e-8, -1e-8), id='abs'),
    pytest.param(Float2((1.0, 1.0)), (1 + 1e-5, 1 - 1e-5), id='rel'),
    pytest.param(Float2((1234.5678, 0.0)), (1234.568, 0), id='usual'),
])
def test_eq(xs, ys):
    assert xs == ys


@pytest.mark.parametrize('sample', [
    pytest.param((3.4028236e+38, 1.0), id='over max'),
    pytest.param((1.0, -3.4028236e+38), id='under min'),
])
def test_out_of_range_raises_value_error(sample):
    with pytest.raises(ValueError) as ei:
        Float2.of(sample)
    print(ei.value)


@pytest.mark.parametrize(['value', 'text'], [
    pytest.param(Float2((1234.5678, 1.25)), 'Float2((1234.568, 1.25))', id='usual')
])
def test_repr(value, text):
    assert repr(value) == text
    assert eval(text) == value
