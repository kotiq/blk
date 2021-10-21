import pytest
from pytest_lazyfixture import lazy_fixture
from blk.binary.constructor import compose_fat_data, serialize_fat_data, Fat


sections_only = lazy_fixture('sections_only')
sections_only_fat_data_istream = lazy_fixture('sections_only_fat_data_istream')
sections_only_fat_data_bs = lazy_fixture('sections_only_fat_data_bs')

all_params = lazy_fixture('all_params')
all_params_fat_data_istream = lazy_fixture('all_params_fat_data_istream')
all_params_fat_data_bs = lazy_fixture('all_params_fat_data_bs')

all_params_fat_s_data_istream = lazy_fixture('all_params_fat_s_data_istream')
all_params_fat_s_data_bs = lazy_fixture('all_params_fat_s_data_bs')

all_params_fat_istream = lazy_fixture('all_params_fat_istream')
all_params_fat_bs = lazy_fixture('all_params_fat_bs')

all_params_fat_s_istream = lazy_fixture('all_params_fat_s_istream')
all_params_fat_s_bs = lazy_fixture('all_params_fat_s_bs')


@pytest.mark.parametrize(['fat_data_istream', 'fat_data_bs', 'section'], [
    pytest.param(
        sections_only_fat_data_istream,
        sections_only_fat_data_bs,
        sections_only,
        id='sections only',
    ),
    pytest.param(
        all_params_fat_data_istream,
        all_params_fat_data_bs,
        all_params,
        id='all_params',
    ),
    pytest.param(
        all_params_fat_s_data_istream,
        all_params_fat_s_data_bs,
        all_params,
        id='all_params_s',
    ),
])
def test_fat_data_parse(fat_data_istream, fat_data_bs, section):
    parsed = compose_fat_data(fat_data_istream)
    assert fat_data_istream.tell() == len(fat_data_bs)
    assert parsed == section


@pytest.mark.parametrize(['section', 'fat_data_bs', 'strings_in_names'], [
    pytest.param(sections_only, sections_only_fat_data_bs, False, id='sections only'),
    pytest.param(all_params, all_params_fat_data_bs, False, id='all_params'),
    pytest.param(all_params, all_params_fat_s_data_bs, True, id='all_params_s'),
])
def test_fat_data_build(section, fat_data_bs, strings_in_names, ostream):
    serialize_fat_data(section, ostream, strings_in_names)
    ostream.seek(0)
    built = ostream.read()
    assert built == fat_data_bs


@pytest.mark.parametrize(['fat_istream', 'fat_bs', 'section'], [
    pytest.param(
        all_params_fat_istream,
        all_params_fat_bs,
        all_params,
        id='all_params',
    ),
    pytest.param(
        all_params_fat_s_istream,
        all_params_fat_s_bs,
        all_params,
        id='all_params_s',
    ),
])
def test_fat_parse(fat_istream, fat_bs, section):
    parsed = Fat.parse_stream(fat_istream)
    assert fat_istream.tell() == len(fat_bs)
    assert parsed == section


@pytest.mark.parametrize(['section', 'fat_bs', 'strings_in_names'], [
    pytest.param(all_params, all_params_fat_bs, False, id='all_params'),
    pytest.param(all_params, all_params_fat_s_bs, True, id='all_params_s'),
])
def test_fat_build(section, fat_bs, strings_in_names, ostream):
    Fat.build_stream(section, ostream, strings_in_names=strings_in_names)
    ostream.seek(0)
    built = ostream.read()
    assert built == fat_bs
