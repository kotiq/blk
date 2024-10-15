from pytest import mark, param as _
from blk.types import Float, Int

DEFAULT = object()


def _test_value(sample, expected):
    assert type(sample) == type(expected)
    assert sample == expected


@mark.parametrize(['name', 'index', 'expected'], [
    _('x', 0, Int(1)),
    _('x', 1, Int(2)),
    _('y', 0, Float(1.0)),
    _('y', 1, Float(2.0)),
])
def test_get(section, name, index, expected):
    value = section.get(name, index, DEFAULT)
    _test_value(value, expected)


def test_get_wrong_name_return_default(section):
    assert section.get('z', 0, DEFAULT) is DEFAULT


def test_get_wrong_index_return_default(section):
    assert section.get('x', 2, DEFAULT) is DEFAULT


@mark.parametrize(['name', 'expected'], [
    _('x', Int(1)),
    _('y', Float(1.0)),
])
def test_get_skip_index_skip_default_return_first_value(section, name, expected):
    value = section.get(name)
    _test_value(value, expected)


def test_get_wrong_name_skip_default_return_none(section):
    assert section.get('z', 0) is None
