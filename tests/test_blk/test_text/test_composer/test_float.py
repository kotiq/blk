import pytest
from pytest import param as _
from blk.types import Float
from blk.text.composer import floating


@pytest.mark.parametrize(['text', 'value'], [
    _('123.456', Float(123.456), id='usual'),
    _('1.23456e+2', Float(123.456), id='scientific e'),
    _('1.23456E+2', Float(123.456), id='scientific E'),
    _('123456', Float(123456), id='integer'),
])
def test_compose_float(text, value):
    parsed = floating.parse(text)
    assert isinstance(parsed, Float)
    assert parsed == value
