from pytest import mark, param as _
from blk.types import Int
from .test_get_int import _test_value

DEFAULT = object()


@mark.parametrize(['name', 'expected'], [
    _('x', Int(1)),
])
def test_get_first_int(section, name, expected):
    value = section.get_first_int(name, DEFAULT)
    _test_value(value, expected)


def test_get_first_int_wrong_name_return_default(section):
    assert section.get_first_int('z', DEFAULT) is DEFAULT


def test_get_first_int_wrong_type_return_default(section):
    assert section.get_first_int('y', DEFAULT) is DEFAULT


@mark.parametrize(['name', 'expected'], [
    _('x', Int(1))
])
def test_get_first_int_skip_default(section, name, expected):
    value = section.get_first_int(name)
    _test_value(value, expected)


def test_get_first_int_wrong_name_skip_default_return_none(section):
    assert section.get_first_int('z') is None
