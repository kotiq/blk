import logging
from pytest import mark, param as _, raises
from blk.types import Str


@mark.parametrize(['sample', 'expected'], [
    _('', '', id='empty'),
    _('hello', 'hello', id='ascii text'),
    _('привет', 'привет', id='utf8 text'),
    _(b'hello', 'hello', id='ascii bytes'),
    _('привет'.encode('utf8'), 'привет', id='utf8 bytes'),
    _('привет'.encode('cp1251'), 'привет', id='cp1251 bytes'),
])
def test_safe_str_factory(safe_str_factory, sample, expected):
    assert safe_str_factory(sample) == expected


@mark.parametrize('sample', [
    _(1, id='int'),
    _(1.0, id='float'),
])
def test_safe_str_factory_non_anystr_raises_type_error(safe_str_factory, sample):
    with raises(TypeError) as ei:
        safe_str_factory(sample)
    logging.info(ei.value)


@mark.parametrize('sample', [
    _(b'\x98', id='0x98 undefined')
])
def test_safe_str_factory_unknown_encoding_raises_value_error(safe_str_factory, sample):
    with raises(ValueError) as ei:
        safe_str_factory(sample)
    logging.info(ei.value)


@mark.parametrize(['value', 'text'], [
    _(Str('Hello'), "Str('Hello')", id='usual')
])
def test_repr(value, text):
    assert repr(value) == text
    assert eval(text) == value
