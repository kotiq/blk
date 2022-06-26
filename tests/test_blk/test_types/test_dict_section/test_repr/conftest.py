import pytest
from blk.types import DictSection, Float2, Float3, Name, Str


@pytest.fixture(scope='module')
def flat_dict_section():
    """DictSection только с одним уровнем."""

    return DictSection([
        (Name('a'), [Float2((1, 2)), Float2((3, 4))]),
        (Name('b'), [Float3((5, 6, 7))]),
        (Name('c'), [Str('hello')]),
    ])


@pytest.fixture(scope='module')
def flat_dict_section_text():
    """repr для flat_dict_section."""

    return ("DictSection([(Name('a'), [Float2((1, 2)), Float2((3, 4))]), (Name('b'), [Float3((5, 6, 7))]), "
            "(Name('c'), [Str('hello')])])")


@pytest.fixture(scope='module')
def nested_dict_section():
    """DictSection с несколькими уровнями."""

    return DictSection([
        (Name('a'), [Str('hello')]),
        (Name('b'), [DictSection([(Name('c'), [Str('nested')])])]),
        (Name('d'), [Str('world')])
    ])


@pytest.fixture(scope='module')
def nested_dict_section_text():
    """repr для nested_dict_section."""

    return ("DictSection([(Name('a'), [Str('hello')]), (Name('b'), [DictSection([(Name('c'), [Str('nested')])])]), "
            "(Name('d'), [Str('world')])])")
