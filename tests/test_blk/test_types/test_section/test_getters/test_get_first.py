from pytest import mark, param as _
from blk.types import Float, Int
from .test_get import _test_value

DEFAULT = object()


@mark.parametrize(['name', 'expected'], [
    _('x', Int(1)),
    _('y', Float(1.0)),
])
def test_get_first(section, name, expected):
    value = section.get_first(name, DEFAULT)
    _test_value(value, expected)


def test_get_first_wrong_name_return_default(section):
    assert section.get_first('z', DEFAULT) is DEFAULT


@mark.parametrize(['name', 'expected'], [
    _('x', Int(1)),
    _('y', Float(1.0)),
])
def test_get_first_skip_default(section, name, expected):
    value = section.get_first(name)
    _test_value(value, expected)


def test_get_first_wrong_name_skip_default_return_none(section):
    assert section.get_first('z') is None
