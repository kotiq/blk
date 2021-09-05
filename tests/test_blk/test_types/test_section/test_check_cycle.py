import itertools as itt
import pytest
from pytest_lazyfixture import lazy_fixture
from blk.types import *


def test_section_with_cycle_sample(section_with_cycle: Section, expected_some_names):
    some_names_it = itt.islice(section_with_cycle.names(), 0, 5)
    some_names = tuple(map(str, some_names_it))
    assert some_names == expected_some_names


@pytest.mark.parametrize(['section', 'has_cycle'], [
    pytest.param(lazy_fixture('section_with_cycle'), True, id='section with cycle'),
    pytest.param(lazy_fixture('section_with_same_id_sub'), False, id='section with same id sub'),
    pytest.param(lazy_fixture('section_with_cycle_deep'), True, id='section with cycle deep'),
    pytest.param(lazy_fixture('section_with_same_id_sub_deep'), False, id='section with same id sub deep'),
])
def test_cycle(section: Section, has_cycle: bool):
    if has_cycle:
        with pytest.raises(CycleError):
            section.check_cycle()
    else:
        section.check_cycle()
