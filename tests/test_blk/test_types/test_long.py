import logging
from pytest import mark, param as _, raises
from blk.types import Long


@mark.parametrize(['sample', 'expected'], [
    _(0x1_0000_0000, 0x1_0000_0000, id='usual'),
    _(0x7fff_ffff_ffff_ffff, 0x7fff_ffff_ffff_ffff, id='max'),
    _(-0x8000_0000_0000_0000, -0x8000_0000_0000_0000, id='min'),
])
def test_safe_long_factory(safe_long_factory, sample, expected):
    assert safe_long_factory(sample) == expected


@mark.parametrize('sample', [
    _(1.0, id='float'),
    _('1', id='str'),
])
def test_of_non_int_raises_type_error(safe_long_factory, sample):
    with raises(TypeError) as ei:
        safe_long_factory(sample)
    logging.info(ei.value)


@mark.parametrize('sample', [
    _(0x8000_0000_0000_0000, id='next max'),
    _(-0x8000_0000_0000_0001, id='prev min'),
])
def test_of_out_of_range_raises_value_error(safe_long_factory, sample):
    with raises(ValueError) as ei:
        safe_long_factory(sample)
    logging.info(ei.value)


@mark.parametrize(['value', 'text'], [
    _(Long(0x1_0000_0000), 'Long(4294967296)', id='usual')
])
def test_repr(value, text):
    assert repr(value) == text
    assert eval(text) == value
