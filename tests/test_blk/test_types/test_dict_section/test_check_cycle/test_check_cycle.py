from itertools import islice
import pytest
from pytest import param as _
from pytest_lazyfixture import lazy_fixture
from blk.types import CycleError


def test_section_with_cycle_sample(dict_section_with_cycle, expected_names):
    names_it = islice(dict_section_with_cycle.names(), 0, 5)
    names = tuple(map(str, names_it))
    assert names == expected_names


@pytest.mark.parametrize(['dict_section', 'has_cycle'], [
    _(lazy_fixture('dict_section_with_cycle'), True, id='cycle'),
    _(lazy_fixture('dict_section_with_same_id_sub'), False, id='same id sub'),
    _(lazy_fixture('dict_section_with_cycle_deep'), True, id='cycle deep'),
    _(lazy_fixture('dict_section_with_same_id_sub_deep'), False, id='same id sub deep'),
])
def test_cycle(dict_section, has_cycle):
    if has_cycle:
        with pytest.raises(CycleError):
            dict_section.check_cycle()
    else:
        dict_section.check_cycle()
