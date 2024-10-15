from importlib import resources
from io import BytesIO
from pytest import fixture
from zstandard import ZstdCompressionDict, ZstdCompressor, ZstdDecompressor
from blk.types import Name
from blk.binary.constructor import InvNames
from samples.section import make_section


@fixture(scope='module')
def samples_dir():
    with resources.path('samples', '') as p:
        return p


@fixture()
def section():
    return make_section()


@fixture(scope='module')
def slim_file_bs(samples_dir):
    return (samples_dir / 'section_slim.blk').read_bytes()


@fixture(scope='module')
def slim_zst_file_bs(samples_dir):
    return (samples_dir / 'section_slim_zst.blk').read_bytes()


@fixture(scope='module')
def slim_zst_dict_file_bs(samples_dir):
    return (samples_dir / 'section_slim_zst_dict.blk').read_bytes()


@fixture(scope='module')
def names():
    return tuple(map(Name.of, ('vec4f', 'int', 'long', 'alpha', 'str', 'bool', 'color', 'gamma', 'vec2i', 'vec2f',
                               'transform', 'beta', 'float', 'vec3f', 'hello')))


@fixture(scope='module')
def inv_names(names):
    return InvNames(names)


@fixture(scope='module')
def no_dict_decompressor():
    return ZstdDecompressor()


@fixture(scope='module')
def no_dict_compressor():
    return ZstdCompressor()


@fixture(scope='module')
def dict_(samples_dir):
    dict_bs = (samples_dir / 'bfb732560ad45234690acad246d7b14c2f25ad418a146e5e7ef68ba3386a315c.dict').read_bytes()
    return ZstdCompressionDict(dict_bs)


@fixture(scope='module')
def dict_compressor(dict_):
    return ZstdCompressor(dict_data=dict_)


@fixture(scope='module')
def dict_decompressor(dict_):
    return ZstdDecompressor(dict_data=dict_)


@fixture()
def slim_file_istream(slim_file_bs):
    return BytesIO(slim_file_bs)


@fixture()
def slim_zst_file_istream(slim_zst_file_bs):
    return BytesIO(slim_zst_file_bs)


@fixture()
def slim_zst_dict_file_istream(slim_zst_dict_file_bs):
    return BytesIO(slim_zst_dict_file_bs)
