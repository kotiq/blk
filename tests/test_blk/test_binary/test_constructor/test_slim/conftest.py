from io import BytesIO
from pathlib import Path
import pytest
from zstandard import ZstdCompressionDict, ZstdCompressor, ZstdDecompressor
import samples
from blk.types import Name
from blk.binary.constructor import InvNames
from samples.section import make_section


@pytest.fixture(scope='module')
def samples_dir():
    return Path(samples.__path__[0])


@pytest.fixture()
def section():
    return make_section()


@pytest.fixture(scope='module')
def slim_file_bs(samples_dir):
    return (samples_dir / 'section_slim.blk').read_bytes()


@pytest.fixture(scope='module')
def slim_zst_file_bs(samples_dir):
    return (samples_dir / 'section_slim_zst.blk').read_bytes()


@pytest.fixture(scope='module')
def slim_zst_dict_file_bs(samples_dir):
    return (samples_dir / 'section_slim_zst_dict.blk').read_bytes()


@pytest.fixture(scope='module')
def names():
    return tuple(map(Name.of, ('vec4f', 'int', 'long', 'alpha', 'str', 'bool', 'color', 'gamma', 'vec2i', 'vec2f',
                               'transform', 'beta', 'float', 'vec3f', 'hello')))


@pytest.fixture(scope='module')
def inv_names(names):
    return InvNames(names)


@pytest.fixture(scope='module')
def no_dict_decompressor():
    return ZstdDecompressor()


@pytest.fixture(scope='module')
def no_dict_compressor():
    return ZstdCompressor()


@pytest.fixture(scope='module')
def dict_(samples_dir):
    dict_bs = (samples_dir / 'bfb732560ad45234690acad246d7b14c2f25ad418a146e5e7ef68ba3386a315c.dict').read_bytes()
    return ZstdCompressionDict(dict_bs)


@pytest.fixture(scope='module')
def dict_compressor(dict_):
    return ZstdCompressor(dict_data=dict_)


@pytest.fixture(scope='module')
def dict_decompressor(dict_):
    return ZstdDecompressor(dict_data=dict_)


@pytest.fixture()
def slim_file_istream(slim_file_bs):
    return BytesIO(slim_file_bs)


@pytest.fixture()
def slim_zst_file_istream(slim_zst_file_bs):
    return BytesIO(slim_zst_file_bs)


@pytest.fixture()
def slim_zst_dict_file_istream(slim_zst_dict_file_bs):
    return BytesIO(slim_zst_dict_file_bs)
