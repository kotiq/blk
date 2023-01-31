from itertools import chain, product
import pytest
from pytest import param as _
from pytest_lazyfixture import lazy_fixture
from blk.format_ import Format
from blk.types import CycleError
from blk.json import serialize

get = globals().__getitem__

bases = ('mixed_dict_section', 'dict_sections_only_dict_section', 'dict_section_with_same_id_sub',
         'dict_section_with_same_id_sub_deep')
formats = ('json_2', )

for fixture_name in chain(bases, (f'json_{"_".join(p)}' for p in product(bases, formats))):
    globals()[fixture_name] = lazy_fixture(fixture_name)

test_serialize_unsorted_cycle_unchecked_params = \
    [_(get(base), Format[fmt.upper()], get(f'json_{base}_{fmt}'), id=f'{base}-{fmt}')
     for base, fmt in product(bases, formats)]


@pytest.mark.parametrize(['dict_section', 'out_type', 'json'], test_serialize_unsorted_cycle_unchecked_params)
def test_serialize_unsorted_cycle_unchecked(dict_section, ostream, out_type, json):
    serialize(dict_section, ostream, out_type, False, False)
    ostream.seek(0)
    assert ostream.read() == json


@pytest.mark.parametrize('check_cycle', [False, True])
@pytest.mark.parametrize('dict_section',  lazy_fixture(['dict_section_with_cycle', 'dict_section_with_cycle_deep']))
def test_serialize_section_with_cycle_unsorted(dict_section, ostream, check_cycle):
    with pytest.raises(CycleError if check_cycle else RecursionError):
        serialize(dict_section, ostream, Format.JSON_2, False, check_cycle)
