import pytest
from pytest import param as _
from blk.types import Float2
from .test_float import approx


@pytest.mark.parametrize(['sample', 'expected'], [
    _((123.456, 789.012), Float2((123.456, 789.012)),  id='usual'),
    _((3.4028235e+38, 1.0), Float2((3.4028235e+38, 1.0)), id='max'),
    _((1.0, -3.4028235e+38), Float2((1.0, -3.4028235e+38)), id='min'),
    _((1.1754944e-38, 1.0), Float2((1.1754944e-38, 1.0)), id='tiny'),
])
def test_of(sample, expected):
    assert all(x == approx(y) for x, y in zip(Float2.of(sample), expected))


@pytest.mark.parametrize('sample', [
    _(('1.0', 1.0), id='str'),
])
def test_of_non_numbers_raises_type_error(sample):
    with pytest.raises(TypeError) as ei:
        Float2.of(sample)
    print(ei.value)


@pytest.mark.parametrize('sample', [
    _((1.0, ), id='less'),
    _((1.0, 2.0, 3.0), id='great'),
])
def test_of_wrong_init_size_raises_type_error(sample):
    with pytest.raises(TypeError) as ei:
        Float2.of(sample)
    print(ei.value)


@pytest.mark.parametrize(['xs', 'ys'], [
    _(Float2((0.0, 0.0)), (1e-8, -1e-8), id='abs'),
    _(Float2((1.0, 1.0)), (1 + 1e-5, 1 - 1e-5), id='rel'),
    _(Float2((1234.5678, 0.0)), (1234.568, 0), id='usual'),
])
def test_eq(xs, ys):
    assert xs == ys


@pytest.mark.parametrize('sample', [
    _((3.4028236e+38, 1.0), id='over max'),
    _((1.0, -3.4028236e+38), id='under min'),
])
def test_out_of_range_raises_value_error(sample):
    with pytest.raises(ValueError) as ei:
        Float2.of(sample)
    print(ei.value)


@pytest.mark.parametrize(['value', 'text'], [
    _(Float2((1234.5678, 1.25)), 'Float2((1234.568, 1.25))', id='usual')
])
def test_repr(value, text):
    assert repr(value) == text
    assert eval(text) == value
