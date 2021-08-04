import os
import pytest
import construct as ct
from vromfs.constructor import parse_file
from helpers import make_outpath

outpath = make_outpath(__name__)


@pytest.mark.parametrize('rpath', [
    'char.vromfs.bin',
    'regional.vromfs.bin',
])
def test_body(binrespath, rpath, outpath):
    path = os.path.join(binrespath, rpath)
    ns = ct.Container()
    m = parse_file(path, ns)

    print('\n', m.header)

    # compressed_out_path = os.path.join(outpath, 'data.zstd')
    # uncompressed_out_path = os.path.join(outpath, 'data')

    # with open(compressed_out_path, 'wb') as ostream:
    #     ostream.write(ns.deobfs_compressed_data)
    #
    # with open(uncompressed_out_path, 'wb') as ostream:
    #     ostream.write(ns.decompressed_data)

    print('\n', m.body)
