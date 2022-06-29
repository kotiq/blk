from itertools import chain, product
import pytest
from pytest import param as _
from pytest_lazyfixture import lazy_fixture
from blk.binary.constructor import Fat, compose_partial_fat, serialize_fat_data

get = globals().__getitem__

bases = ('dict_sections_only_dict_section', 'all_params_dict_section')
formats = ('fat', 'fat_s')
artifacts = ('istream', 'bs')

for fixture_name in chain(
    bases,
    (f'dict_sections_only_dict_section_fat_data_{artifact}' for artifact in artifacts),
    (f'all_params_dict_section_{fmt}_data_{artifact}' for fmt, artifact in product(formats, artifacts)),
    (f'all_params_dict_section_{fmt}_{artifact}' for fmt, artifact in product(formats, artifacts)),
):
    globals()[fixture_name] = lazy_fixture(fixture_name)

test_fat_data_parse_params =\
[_(get(f'{base}_{fmt}_data_istream'), get(f'{base}_{fmt}_data_bs'), get(base), id=f'{base}_data-{fmt}') for base, fmt in
 chain([('dict_sections_only_dict_section', 'fat')], (('all_params_dict_section', fmt) for fmt in formats))]


@pytest.mark.parametrize(['fat_data_istream', 'fat_data_bs', 'dict_section'], test_fat_data_parse_params)
def test_fat_data_parse(fat_data_istream, fat_data_bs, dict_section):
    parsed = compose_partial_fat(fat_data_istream)
    assert fat_data_istream.tell() == len(fat_data_bs)
    assert parsed == dict_section


test_fat_data_build_params =\
[_(get(base), get(f'{base}_{fmt}_data_bs'), fmt == 'fat_s', id=f'{base}_{fmt}') for base, fmt in
 chain([('dict_sections_only_dict_section', 'fat')], (('all_params_dict_section', fmt) for fmt in formats))]


@pytest.mark.parametrize(['dict_section', 'fat_data_bs', 'strings_in_names'], test_fat_data_build_params)
def test_fat_data_build(dict_section, fat_data_bs, strings_in_names, ostream):
    serialize_fat_data(dict_section, ostream, strings_in_names)
    ostream.seek(0)
    built = ostream.read()
    assert built == fat_data_bs


test_fat_parse_params =\
[_(get(f'{base}_{fmt}_istream'), get(f'{base}_{fmt}_bs'), get(base), id=f'{base}-{fmt}') for base, fmt
 in product(['all_params_dict_section'], formats)]


@pytest.mark.parametrize(['fat_istream', 'fat_bs', 'dict_section'], test_fat_parse_params)
def test_fat_parse(fat_istream, fat_bs, dict_section):
    parsed = Fat.parse_stream(fat_istream)
    assert fat_istream.tell() == len(fat_bs)
    assert parsed == dict_section


test_fat_build_params =\
[_(get(base), get(f'{base}_{fmt}_bs'), fmt == 'fat_s', id=f'{base}-{fmt}') for base, fmt
 in product(['all_params_dict_section'], formats)]


@pytest.mark.parametrize(['dict_section', 'fat_bs', 'strings_in_names'], test_fat_build_params)
def test_fat_build(dict_section, fat_bs, strings_in_names, ostream):
    Fat.build_stream(dict_section, ostream, strings_in_names=strings_in_names)
    ostream.seek(0)
    built = ostream.read()
    assert built == fat_bs
