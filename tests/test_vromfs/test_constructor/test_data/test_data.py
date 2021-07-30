import os
import pytest
import construct as ct
from vromfs.constructor import parse_file
from helpers import outdir_rpath

outdir_rpath = outdir_rpath(__name__)


@pytest.mark.parametrize('rpath', [
    'char.vromfs.bin',
])
def test_body(binrespath, rpath, buildpath):
    path = os.path.join(binrespath, rpath)
    ns = ct.Container()
    m = parse_file(path, ns)

    outdir_path = os.path.join(buildpath, outdir_rpath)
    os.makedirs(outdir_path, exist_ok=True)

    compressed_out_path = os.path.join(outdir_path, 'data.zstd')
    uncompressed_out_path = os.path.join(outdir_path, 'data')

    with open(compressed_out_path, 'wb') as ostream:
        ostream.write(ns.deobfs_compressed_data)

    with open(uncompressed_out_path, 'wb') as ostream:
        ostream.write(ns.decompressed_data)

    print('\n', m.body)
