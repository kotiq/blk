from http.client import responses
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
def fat_file_bs(samples_dir):
    return (samples_dir / 'section_fat.blk').read_bytes()


@fixture(scope='module')
def fat_s_file_bs(samples_dir):
    return (samples_dir / 'section_fat_s.blk').read_bytes()


@fixture()
def fat_file_istream(fat_file_bs):
    return BytesIO(fat_file_bs)


@fixture()
def fat_s_file_istream(fat_s_file_bs):
    return BytesIO(fat_s_file_bs)
