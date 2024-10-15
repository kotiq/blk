import logging
from pytest import mark, param as _, raises
from blk.types import UByte


@mark.parametrize(['sample', 'expected'], [
    _(18, 18, id='usual'),
    _(0xff, 0xff, id='max'),
    _(0, 0, id='min'),
])
def test_safe_ubyte_factory(safe_ubyte_factory, sample, expected):
    assert safe_ubyte_factory(sample) == expected


@mark.parametrize('sample', [
    _(1.0, id='float'),
    _('1', id='str')
])
def test_safe_ubyte_factory_non_int_raises_type_error(safe_ubyte_factory, sample):
    with raises(TypeError) as ei:
        safe_ubyte_factory(sample)
    logging.info(ei.value)


@mark.parametrize('sample', [
    _(0x100, id='next max'),
    _(-1, id='prev min'),
])
def test_safe_ubyte_factory_out_of_range_raises_value_error(safe_ubyte_factory, sample):
    with raises(ValueError) as ei:
        safe_ubyte_factory(sample)
    logging.info(ei.value)


@mark.parametrize(['value', 'text'], [
    _(UByte(0x12), 'UByte(18)', id='usual')
])
def test_repr(value, text):
    assert repr(value) == text
    assert eval(text) == value
