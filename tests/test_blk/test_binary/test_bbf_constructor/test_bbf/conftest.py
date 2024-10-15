from importlib import resources
from io import BytesIO
from pytest import fixture
from samples.section import make_section


@fixture(scope='module')
def samples_dir():
    with resources.path('samples', '') as p:
        return p


@fixture()
def section():
    return make_section()


@fixture(scope='module')
def bbf_file_bs(samples_dir):
    return (samples_dir / 'section_bbf.blk').read_bytes()


@fixture()
def bbf_file_istream(bbf_file_bs):
    return BytesIO(bbf_file_bs)
