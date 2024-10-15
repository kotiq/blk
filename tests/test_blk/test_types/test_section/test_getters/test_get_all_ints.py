from pytest import mark, param as _
from blk.types import Int

DEFAULT = object()


def _test_multivalue(sample, expected):
    assert isinstance(sample, list)
    assert all(isinstance(v, Int) for v in sample)
    assert sample == expected


@mark.parametrize(['name', 'expected'], [
    _('x', [Int(1), Int(2)]),
])
def test_get_all_ints(section, name, expected):
    values = section.get_all_ints(name, DEFAULT)
    _test_multivalue(values, expected)


def test_get_all_ints_wrong_name_return_default(section):
    assert section.get_all_ints('z', DEFAULT) is DEFAULT


def test_get_all_ints_wrong_type_return_default(section):
    assert section.get_all_ints('y', DEFAULT) is DEFAULT


@mark.parametrize(['name', 'expected'], [
    _('x', [Int(1), Int(2)]),
])
def test_get_all_ints_skip_default(section, name, expected):
    values = section.get_all_ints(name)
    _test_multivalue(values, expected)


def test_get_all_ints_wrong_name_skip_default_return_none(section):
    assert section.get_all_ints('z') == []
