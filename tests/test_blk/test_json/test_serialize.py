import io
import pytest
from pytest_lazyfixture import lazy_fixture
from blk.types import CycleError
import blk.json as jsn


@pytest.fixture()
def ostream():
    return io.StringIO()


mixed_section = lazy_fixture('mixed_section')
sections_only_section = lazy_fixture('sections_only_section')
section_with_same_id_sub = lazy_fixture('section_with_same_id_sub')
section_with_same_id_sub_deep = lazy_fixture('section_with_same_id_sub_deep')
json_mixed_json_2 = lazy_fixture('json_mixed_json_2')
json_sections_only_json_2 = lazy_fixture('json_sections_only_json_2')
json_section_with_same_id_sub_json_2 = lazy_fixture('json_section_with_same_id_sub_json_2')
json_section_with_same_id_sub_deep_json_2 = lazy_fixture('json_section_with_same_id_sub_deep_json_2')


@pytest.mark.parametrize(['section', 'out_type', 'section_json'], [
    pytest.param(mixed_section, jsn.JSON_2, json_mixed_json_2, id='mixed-json_2'),
    pytest.param(sections_only_section, jsn.JSON_2, json_sections_only_json_2, id='sections only-json_2'),
    pytest.param(section_with_same_id_sub, jsn.JSON_2, json_section_with_same_id_sub_json_2,
                id='same id sub-json_2'),
    pytest.param(section_with_same_id_sub_deep, jsn.JSON_2, json_section_with_same_id_sub_deep_json_2,
                 id='same id sub deep-json_2'),
])
def test_serialize_unsorted_cycle_unchecked(section, ostream, out_type, section_json):
    is_sorted = False
    check_cycle = False
    jsn.serialize(section, ostream, out_type, is_sorted, check_cycle)
    ostream.seek(0)
    json = ostream.read()
    assert json == section_json


section_with_cycle = lazy_fixture('section_with_cycle')
section_with_cycle_deep = lazy_fixture('section_with_cycle_deep')


@pytest.mark.parametrize('check_cycle', [False, True])
@pytest.mark.parametrize('section', [
    section_with_cycle,
    section_with_cycle_deep
])
def test_serialize_section_with_cycle_unsorted(section, ostream, check_cycle):
    is_sorted = False
    out_type = jsn.JSON_2
    if check_cycle:
        with pytest.raises(CycleError):
            jsn.serialize(section, ostream, out_type, is_sorted, check_cycle)
    else:
        with pytest.raises(RecursionError):
            jsn.serialize(section, ostream, out_type, is_sorted, check_cycle)
