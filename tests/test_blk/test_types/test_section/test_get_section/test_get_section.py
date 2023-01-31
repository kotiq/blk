from blk.types import Int, Name, Section


DEFAULT = object()


def test_get_first_section(section: Section):
    value = section.get_section('a', index=0)
    assert type(value) is type(section)
    assert list(value.pairs()) == [(Name('x'), Int(1))]


def test_get_all_sections(section: Section):
    values = section.get_section('a', index=None)
    assert type(values[0]) is type(section)
    assert list(values[0].pairs()) == [(Name('x'), Int(1))]
    assert list(values[1].pairs()) == [(Name('y'), Int(2))]


def test_get_first_section_wrong_name_return_default(section: Section):
    assert section.get_section('c', index=0, default=DEFAULT) is DEFAULT


def test_get_first_section_wrong_value_type_return_default(section: Section):
    assert section.get_section('x', index=0, default=DEFAULT) is DEFAULT


def test_get_section_wrong_index_return_default(section: Section):
    assert section.get_section('a', index=2, default=DEFAULT) is DEFAULT
