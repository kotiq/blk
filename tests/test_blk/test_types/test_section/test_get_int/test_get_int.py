from blk.types import Int, Section


DEFAULT = object()


def test_get_first_int(section: Section):
    assert section.get_int('x', index=0) == Int(1)


def test_get_all_ints(section: Section):
    assert list(section.get_int('x', index=None)) == [Int(1), Int(2)]


def test_get_first_int_wrong_name_return_default(section: Section):
    assert section.get_int('z', index=0, default=DEFAULT) is DEFAULT


def test_get_first_int_wrong_value_type_return_default(section: Section):
    assert section.get_int('y', index=0, default=DEFAULT) is DEFAULT


def test_get_int_wrong_index_return_default(section: Section):
    assert section.get_int('x', index=2, default=DEFAULT) is DEFAULT
