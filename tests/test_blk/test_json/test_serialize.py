from itertools import chain, product
from pytest import mark, param as _, raises
from pytest_lazyfixture import lazy_fixture as lf
from blk.format_ import Format
from blk.types import CycleError
from blk.json import serialize
from test_blk.test_json.test_serializer.test_section import _test_json_like

get = globals().__getitem__

bases = (
    'mixed_dict_section',
    'dict_sections_only_dict_section',
    'dict_section_with_same_id_sub',
    'dict_section_with_same_id_sub_deep',
)
formats = (
    'json_2',
)

for fixture_name in chain(bases, (f'json_{"_".join(p)}' for p in product(bases, formats))):
    globals()[fixture_name] = lf(fixture_name)

test_serialize_unsorted_cycle_unchecked_params = \
    [_(get(base), Format[fmt.upper()], get(f'json_{base}_{fmt}'), id=f'{base}-{fmt}')
     for base, fmt in product(bases, formats)]


@mark.parametrize(['dict_section', 'out_format', 'json'], test_serialize_unsorted_cycle_unchecked_params)
def test_serialize_unsorted_not_minified_cycle_unchecked(dict_section, ostream, out_format, json):
    serialize(dict_section, ostream, out_format=out_format, is_minified=False, is_sorted=False, check_cycle=False)
    ostream.seek(0)
    _test_json_like(ostream.read(), json)


@mark.parametrize('check_cycle', [
    _(False, id='unchecked'),
    _(True, id='checked')
])
@mark.parametrize('dict_section', lf([
    'dict_section_with_cycle',
    'dict_section_with_cycle_deep'
]))
def test_serialize_section_with_cycle_unsorted(dict_section, ostream, check_cycle):
    with raises(CycleError if check_cycle else RecursionError):
        serialize(dict_section, ostream, out_format=Format.JSON_2, is_sorted=False, check_cycle=check_cycle)
