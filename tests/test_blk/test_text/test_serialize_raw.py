import pytest
from pytest_lazyfixture import lazy_fixture
import blk.text as txt

section_single_level = lazy_fixture('section_single_level')
section_multi_level = lazy_fixture('section_multi_level')
text_single_level_default = lazy_fixture('text_single_level_default')
text_multi_level_default = lazy_fixture('text_multi_level_default')


@pytest.mark.parametrize(['section', 'dialect', 'section_text'], [
    pytest.param(section_single_level, txt.DefaultDialect, text_single_level_default, id='single_level-default'),
    pytest.param(section_multi_level, txt.DefaultDialect, text_multi_level_default, id='multi_level-default')
])
def test_serialize(section, ostream, dialect, section_text):
    txt.serialize(section, ostream, dialect)
    ostream.seek(0)
    text = ostream.read()
    assert text == section_text
