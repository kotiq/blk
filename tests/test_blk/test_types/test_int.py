import logging
from pytest import mark, param as _, raises
from blk.types import Int


@mark.parametrize(['sample', 'expected'], [
    _(1024, 1024, id='usual'),
    _(0x7fff_ffff, 0x7fff_ffff, id='max'),
    _(-0x8000_0000, -0x8000_0000, id='min'),
])
def test_safe_int_factory(safe_int_factory, sample, expected):
    assert safe_int_factory(sample) == expected


@mark.parametrize('sample', [
    _(1.0, id='float'),
    _('1', id='str'),
])
def test_safe_int_factory_non_int_raises_type_error(safe_int_factory, sample):
    with raises(TypeError) as ei:
        safe_int_factory(sample)
    logging.info(ei.value)


@mark.parametrize('sample', [
    _(0x8000_0000, id='next max'),
    _(-0x8000_0001, id='prev min'),
])
def test_safe_int_factory_out_of_range_raises_value_error(safe_int_factory, sample):
    with raises(ValueError) as ei:
        safe_int_factory(sample)
    logging.info(ei.value)


@mark.parametrize(['value', 'text'], [
    _(Int(1024), 'Int(1024)', id='usual')
])
def test_repr(value, text):
    assert repr(value) == text
    assert eval(text) == value
