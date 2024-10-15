from functools import partial
import logging
from pytest import approx, mark, param as _, raises
from blk.types import Float

approx = partial(approx, rel=1e-05, abs=1e-08)


def rational_sig_figs(s):
    e_pos = s.rfind('e')
    if e_pos != -1:
        s = s[:e_pos]

    return len(s.replace('.', '').lstrip('0'))


@mark.parametrize(['sample', 'expected'], [
    _(123.456, 123.456, id='usual'),
    _(3.4028235e+38, 3.4028235e+38, id='max'),
    _(-3.4028235e+38, -3.4028235e+38, id='min'),
    _(1.1754944e-38, 1.1754944e-38, id='tiny'),
])
def test_safe_float_factory(safe_float_factory, sample, expected):
    assert safe_float_factory(sample) == approx(expected)


@mark.parametrize('sample', [
    _('1.0', id='str'),
])
def test_safe_float_factory_non_number_raises_type_error(safe_float_factory, sample):
    with raises(TypeError) as ei:
        safe_float_factory(sample)
    logging.info(ei.value)


@mark.parametrize('sample', [
    _(3.4028236e+38, id='over max'),
    _(-3.4028236e+38, id='under min'),
])
def test_safe_float_factory_out_of_range_raises_value_error(safe_float_factory, sample):
    with raises(ValueError) as ei:
        safe_float_factory(sample)
    logging.info(ei.value)


@mark.parametrize(['x', 'y'], [
    _(Float(0.0), 1e-8, id='abs'),
    _(Float(1.0), 1 + 1e-5, id='rel'),
    _(Float(1234.5678), 1234.568, id='usual'),
])
def test_close_to(x, y):
    assert x.close_to(y)


@mark.parametrize(['value', 'string'], [
    _(Float(1234.568), '1234.568', id='7 sig figs'),
    _(Float(1234.5678), '1234.568', id='8 sig figs'),
])
def test_repr(value, string):
    text = f'Float({string})'
    assert repr(value) == text
    x = eval(text)
    assert x == value if rational_sig_figs(text) < 7 else x.close_to(value)
