from pytest import mark, param as _
from blk.types import Int

DEFAULT = object()


def _test_value(sample, expected):
    assert isinstance(sample, Int)
    assert sample == expected


@mark.parametrize(['name', 'index', 'expected'], [
    _('x', 0, Int(1)),
    _('x', 1, Int(2)),
])
def gest_get_int(section, name, index, expected):
    value = section.get_int(name, index, DEFAULT)
    _test_value(value, expected)


def test_get_int_wrong_name_return_default(section):
    assert section.get_int('z', 0, DEFAULT) is DEFAULT


def test_get_int_wrong_index_return_default(section):
    assert section.get_int('x', 2, DEFAULT) is DEFAULT


def test_get_int_wrong_type_return_default(section):
    assert section.get_int('y', 0, DEFAULT) is DEFAULT


@mark.parametrize(['name', 'expected'], [
    _('x', Int(1)),
])
def test_get_int_skip_index_skip_default_return_first_value(section, name, expected):
    value = section.get_int(name)
    _test_value(value, expected)


def test_get_int_wrong_name_skip_default_return_none(section):
    assert section.get_int('z', 0) is None
