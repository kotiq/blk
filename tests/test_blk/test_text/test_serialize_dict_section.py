from itertools import chain, product
import pytest
from pytest import param as _
from pytest_lazyfixture import lazy_fixture
from blk.types import CycleError
from blk.text import DefaultDialect, StrictDialect, serialize

get = globals().__getitem__

bases = ('mixed_dict_section', 'dict_sections_only_dict_section')
bases_default = ('dict_section_with_same_id_sub', 'dict_section_with_same_id_sub_deep')
dialects = {
    'default': DefaultDialect,
    'strict': StrictDialect
}

for fixture_name in chain(
        bases,
        bases_default,
        (f'text_{base}_default' for base in bases_default),
        (f'text_{"_".join(p)}' for p in product(bases, dialects))
):
    globals()[fixture_name] = lazy_fixture(fixture_name)

test_serialize_cycle_unchecked_params = \
    [_(get(base), dialects[dialect], get(f'text_{base}_{dialect}'), id=f'{base}-{dialect}')
     for base, dialect in product(bases, dialects)] + \
    [_(get(base), DefaultDialect, get(f'text_{base}_default'), id=f'{base}-default')
     for base in bases_default]


@pytest.mark.parametrize(['dict_section', 'dialect', 'text'], test_serialize_cycle_unchecked_params)
def test_serialize_cycle_unchecked(dict_section, ostream, dialect, text):
    serialize(dict_section, ostream, dialect, False)
    ostream.seek(0)
    assert ostream.read() == text


@pytest.mark.parametrize('check_cycle', [False, True])
@pytest.mark.parametrize('dict_section', lazy_fixture(['dict_section_with_cycle', 'dict_section_with_cycle_deep']))
def test_serialize_dict_section_with_cycle(dict_section, ostream, check_cycle):
    with pytest.raises(CycleError if check_cycle else RecursionError):
        serialize(dict_section, ostream, DefaultDialect, check_cycle)
