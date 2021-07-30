import pytest
from blk.types import *
from .sections import flat_section, nested_section


flat_section_repr = ("Section([(Name('a'), [Float2((1, 2)), Float2((3, 4))]), (Name('b'), [Float3((5, 6, 7))]), "
                     "(Name('c'), [Str('hello')])])")

nested_section_repr = ("Section([(Name('a'), [Str('hello')]), (Name('b'), [Section([(Name('c'), [Str('nested')])])]), "
                       "(Name('d'), [Str('world')])])")


@pytest.mark.parametrize(['section', 'expected'], [
    pytest.param(flat_section, flat_section_repr, id='flat'),
    pytest.param(nested_section, nested_section_repr, id='nested'),
])
def test_repr_flat_section(section, expected):
    assert repr(section) == expected


@pytest.mark.parametrize(['section', 'expected'], [
    pytest.param(flat_section, flat_section_repr, id='flat'),
    pytest.param(nested_section, nested_section_repr, id='nested'),
])
def test_eval_flat_section_repr(section, expected):
    assert eval(expected) == section
