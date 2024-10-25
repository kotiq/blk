from pytest import mark, param as _
from blk.types import Float, Int, Name, Section

DEFAULT = object()

def _test_multivalue(sample, expected):
    assert isinstance(sample, list)
    assert all(isinstance(v, Section) for v in sample)
    for sec, pairs in zip(sample, expected):
        assert list(sec.pairs()) == pairs


@mark.parametrize(['name', 'expected'], [
    _('map', [
        [(Name('x'), Int(1))],
        [(Name('y'), Float(1.0))],
    ]),
])
def test_all_sections(section, name, expected):
    values = section.get_all_sections(name, DEFAULT)
    _test_multivalue(values, expected)


def test_get_all_sections_wrong_name_return_default(section):
    assert section.get_all_sections('map_', DEFAULT) is DEFAULT


def test_get_all_sections_wrong_type_return_default(section):
    assert section.get_all_sections('x', DEFAULT) is DEFAULT


@mark.parametrize(['name', 'expected'], [
    _('map', [
        [(Name('x'), Int(1))],
        [(Name('y'), Float(1.0))],
    ]),
])
def test_all_sections_skip_default(section, name, expected):
    values = section.get_all_sections(name)
    _test_multivalue(values, expected)


def test_get_all_sections_wrong_name_skip_default_return_empty_list(section):
    assert section.get_all_sections('x') == []
