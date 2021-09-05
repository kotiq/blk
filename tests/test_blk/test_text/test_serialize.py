import io
import pytest
from pytest_lazyfixture import lazy_fixture
from blk.types import CycleError
import blk.text as txt


@pytest.fixture()
def ostream():
    return io.StringIO()


mixed_section = lazy_fixture('mixed_section')
sections_only_section = lazy_fixture('sections_only_section')
section_with_same_id_sub = lazy_fixture('section_with_same_id_sub')
section_with_same_id_sub_deep = lazy_fixture('section_with_same_id_sub_deep')
text_mixed_default = lazy_fixture('text_mixed_default')
text_mixed_strict = lazy_fixture('text_mixed_strict')
text_sections_only_default = lazy_fixture('text_sections_only_default')
text_sections_only_strict = lazy_fixture('text_sections_only_strict')
text_section_with_same_id_sub_default = lazy_fixture('text_section_with_same_id_sub_default')
text_section_with_same_id_sub_deep_default = lazy_fixture('text_section_with_same_id_sub_deep_default')


@pytest.mark.parametrize(['section', 'dialect', 'section_text'], [
    pytest.param(mixed_section, txt.DefaultDialect, text_mixed_default, id='mixed-default'),
    pytest.param(mixed_section, txt.StrictDialect, text_mixed_strict, id='mixed-strict'),
    pytest.param(sections_only_section, txt.DefaultDialect, text_sections_only_default, id='sections only-default'),
    pytest.param(sections_only_section, txt.StrictDialect, text_sections_only_strict, id='sections only-strict'),
    pytest.param(section_with_same_id_sub, txt.DefaultDialect, text_section_with_same_id_sub_default,
                 id='same id sub-default'),
    pytest.param(section_with_same_id_sub_deep, txt.DefaultDialect, text_section_with_same_id_sub_deep_default,
                 id='same id sub deep-default'),
])
def test_serialize_cycle_unchecked(section, ostream, dialect, section_text):
    check_cycle = False
    txt.serialize(section, ostream, dialect, check_cycle)
    ostream.seek(0)
    text = ostream.read()
    assert text == section_text


section_with_cycle = lazy_fixture('section_with_cycle')
section_with_cycle_deep = lazy_fixture('section_with_cycle_deep')


@pytest.mark.parametrize('check_cycle', [False, True])
@pytest.mark.parametrize('section', [
    section_with_cycle,
    section_with_cycle_deep
])
def test_serialize_section_with_cycle(section, ostream, check_cycle):
    dialect = txt.DefaultDialect
    if check_cycle:
        with pytest.raises(CycleError):
            txt.serialize(section, ostream, dialect, check_cycle)
    else:
        with pytest.raises(RecursionError):
            txt.serialize(section, ostream, dialect, check_cycle)
