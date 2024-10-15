from pytest import mark, param as _
from blk.types import Float, Int

DEFAULT = object()


def _test_multivalue(sample, expected):
    assert isinstance(sample, list)
    type_ = type(sample[0])
    assert all(type(v) == type_ for v in sample)
    assert sample == expected


@mark.parametrize(['name', 'expected'], [
    _('x', [Int(1), Int(2)]),
    _('y', [Float(1.0), Float(2.0)]),
])
def test_get_all(section, name, expected):
    values = section.get_all(name, DEFAULT)
    _test_multivalue(values, expected)


def test_get_all_wrong_name_return_default(section):
    assert section.get_all('z', DEFAULT) is DEFAULT


@mark.parametrize(['name', 'expected'], [
    _('x', [Int(1), Int(2)]),
    _('y', [Float(1.0), Float(2.0)]),
])
def test_get_all_skip_default(section, name, expected):
    values = section.get_all(name)
    _test_multivalue(values, expected)


def test_get_all_wrong_name_skip_default_return_empty_list(section):
    assert section.get_all('z') == []

