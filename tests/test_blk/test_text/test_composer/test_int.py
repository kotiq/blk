import pytest
from pytest import param as _
from blk.types import Int, Long, UByte
from blk.text.composer import integer, long, ubyte


@pytest.mark.parametrize(['text', 'value'], [
    _('1024', Int(1024), id='unsigned dec'),
    _('+1024', Int(1024), id='pos dec'),
    _('-1024', Int(-1024), id='neg dec'),
    _('0x1000', Int(0x1000), id='unsigned hex')
])
def test_compose_integer(text, value):
    parsed = integer.parse(text)
    assert isinstance(parsed, Int)
    assert parsed == value


@pytest.mark.parametrize(['text', 'value'], [
    _('1024', Long(1024), id='unsigned dec'),
    _('+1024', Long(1024), id='signed pos dec'),
    _('-1024', Long(-1024), id='signed neg dec'),
    _('0x1000', Long(0x1000), id='unsigned hex'),
])
def test_compose_long(text, value):
    parsed = long.parse(text)
    assert isinstance(parsed, Long)
    assert parsed == value


@pytest.mark.parametrize(['text', 'value'], [
    _('127', UByte(127), id='unsigned dec'),
    _('+127', UByte(127), id='signed dec'),
    _('0xff', UByte(0xff), id='unsigned hex'),
])
def test_compose_ubyte(text, value):
    parsed = ubyte.parse(text)
    assert isinstance(parsed, UByte)
    assert parsed == value
