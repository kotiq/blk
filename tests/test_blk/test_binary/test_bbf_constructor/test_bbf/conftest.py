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
def bbf_file_bs(samples_dir):
    return (samples_dir / 'section_bbf.blk').read_bytes()


@pytest.fixture()
def bbf_file_istream(bbf_file_bs):
    return BytesIO(bbf_file_bs)
