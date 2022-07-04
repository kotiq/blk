from io import BytesIO
from pathlib import Path
import pytest
import samples
from samples.section import make_section


@pytest.fixture(scope='module')
def samples_dir():
    return Path(samples.__path__[0])


@pytest.fixture()
def section():
    return make_section()


@pytest.fixture(scope='module')
def fat_file_bs(samples_dir):
    return (samples_dir / 'section_fat.blk').read_bytes()


@pytest.fixture(scope='module')
def fat_s_file_bs(samples_dir):
    return (samples_dir / 'section_fat_s.blk').read_bytes()


@pytest.fixture()
def fat_file_istream(fat_file_bs):
    return BytesIO(fat_file_bs)


@pytest.fixture()
def fat_s_file_istream(fat_s_file_bs):
    return BytesIO(fat_s_file_bs)
