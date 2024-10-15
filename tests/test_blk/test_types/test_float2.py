import logging
from pytest import mark, param as _, raises
from blk.types import Float2
from .test_float import approx, rational_sig_figs


@mark.parametrize(['sample', 'expected'], [
    _((123.456, 789.012), Float2((123.456, 789.012)), id='usual'),
    _((3.4028235e+38, 1.0), Float2((3.4028235e+38, 1.0)), id='max'),
    _((1.0, -3.4028235e+38), Float2((1.0, -3.4028235e+38)), id='min'),
    _((1.1754944e-38, 1.0), Float2((1.1754944e-38, 1.0)), id='tiny'),
])
def test_safe_float2_factory(safe_float2_factory, sample, expected):
    assert all(x == approx(y) for x, y in zip(safe_float2_factory(sample), expected))


@mark.parametrize('sample', [
    _(('1.0', 1.0), id='str'),
])
def test_safe_float2_factory_non_numbers_raises_type_error(safe_float2_factory, sample):
    with raises(TypeError) as ei:
        safe_float2_factory(sample)
    logging.info(ei.value)


@mark.parametrize('sample', [
    _((1.0,), id='less'),
    _((1.0, 2.0, 3.0), id='great'),
])
def test_safe_float_factory_wrong_init_size_raises_type_error(safe_float2_factory, sample):
    with raises(TypeError) as ei:
        safe_float2_factory(sample)
    logging.info(ei.value)


@mark.parametrize('sample', [
    _((3.4028236e+38, 1.0), id='over max'),
    _((1.0, -3.4028236e+38), id='under min'),
])
def test_safe_float2_factory_out_of_range_raises_value_error(safe_float2_factory, sample):
    with raises(ValueError) as ei:
        safe_float2_factory(sample)
    logging.info(ei.value)


@mark.parametrize(['xs', 'ys'], [
    _(Float2((0.0, 0.0)), (1e-8, -1e-8), id='abs'),
    _(Float2((1.0, 1.0)), (1 + 1e-5, 1 - 1e-5), id='rel'),
    _(Float2((1234.5678, 0.0)), (1234.568, 0), id='usual'),
])
def test_close_to(xs, ys):
    assert xs.close_to(ys)


@mark.parametrize(['value', 'strings'], [
    _(Float2((1234.568, 1.25)), ('1234.568', '1.25'), id='7 sig figs'),
    _(Float2((1234.5678, 1.25)), ('1234.568', '1.25'), id='8 sig figs'),
])
def test_repr(value, strings):
    text = f'Float2(({", ".join(strings)}))'
    assert repr(value) == text
    xs = eval(text)
    assert xs == value if all(rational_sig_figs(s) < 7 for s in strings) else xs.close_to(value)
