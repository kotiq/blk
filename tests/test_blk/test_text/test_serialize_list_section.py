from itertools import chain
import pytest
from pytest import param as _
from pytest_lazyfixture import lazy_fixture
from blk.text import DefaultDialect, serialize

get = globals().__getitem__
bases_default = ('list_section_single_level', 'list_section_multi_level',)

for fixture_name in chain(bases_default, (f'text_{base}_default' for base in bases_default)):
    globals()[fixture_name] = lazy_fixture(fixture_name)

test_serialize_params = \
    [_(get(base), DefaultDialect, get(f'text_{base}_default'), id=f'{base}-default') for base in bases_default]


@pytest.mark.parametrize(['dict_section', 'dialect', 'text'], test_serialize_params)
def test_serialize(dict_section, ostream, dialect, text):
    serialize(dict_section, ostream, dialect)
    ostream.seek(0)
    assert ostream.read() == text
