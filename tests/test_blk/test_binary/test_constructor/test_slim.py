import pytest
from pytest_lazyfixture import lazy_fixture
from blk.binary.constructor import compose_slim_data, serialize_slim_data, Slim

all_params = lazy_fixture('all_params')
all_params_slim_data_bs = lazy_fixture('all_params_slim_data_bs')
all_params_slim_data_istream = lazy_fixture('all_params_slim_data_istream')
all_params_names_seq = lazy_fixture('all_params_names_seq')
all_params_inv_names = lazy_fixture('all_params_inv_names')

all_params_slim_bs = lazy_fixture('all_params_slim_bs')
all_params_slim_istream = lazy_fixture('all_params_slim_istream')


@pytest.mark.parametrize(['slim_data_istream', 'names', 'slim_data_bs', 'section'], [
    pytest.param(
        all_params_slim_data_istream,
        all_params_names_seq,
        all_params_slim_data_bs,
        all_params,
        id='all_params',
    ),
])
def test_slim_data_parse(slim_data_istream, names, slim_data_bs, section):
    parsed = compose_slim_data(names, slim_data_istream)
    assert slim_data_istream.tell() == len(slim_data_bs)
    assert parsed == section


@pytest.mark.parametrize(['section', 'inv_names', 'slim_data_bs'], [
    pytest.param(
        all_params,
        all_params_inv_names,
        all_params_slim_data_bs,
        id='all_params',
    ),
])
def test_slim_data_build(section, inv_names, slim_data_bs, empty_inv_names, ostream):
    inv_nm = empty_inv_names
    serialize_slim_data(section, inv_nm, ostream)
    ostream.seek(0)
    built = ostream.read()
    assert built == slim_data_bs
    assert inv_nm == inv_names


@pytest.mark.parametrize(['slim_istream', 'names', 'slim_bs', 'section'], [
    pytest.param(
        all_params_slim_istream,
        all_params_names_seq,
        all_params_slim_bs,
        all_params,
        id='all_params',
    ),
])
def test_slim_parse(slim_istream, names, slim_bs, section):
    parsed = Slim.parse_stream(slim_istream, names_or_inv_names=names)
    assert slim_istream.tell() == len(slim_bs)
    assert parsed == section


@pytest.mark.parametrize(['section', 'inv_names', 'slim_bs'], [
    pytest.param(
        all_params,
        all_params_inv_names,
        all_params_slim_bs,
        id='all_params',
    ),
])
def test_slim_build(section, inv_names, slim_bs, empty_inv_names, ostream):
    inv_nm = empty_inv_names
    Slim.build_stream(section, ostream, names_or_inv_names=inv_nm)
    ostream.seek(0)
    built = ostream.read()
    assert built == slim_bs
    assert inv_nm == inv_names
