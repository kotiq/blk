import os
import sys
import pytest
from helpers import make_outpath
import demo

demo_prefix = demo.__path__[0]
outpath = make_outpath(__name__)


@pytest.mark.parametrize('format_', [
    'strict_blk',
    'json',
    'json_2',
])
def test_strict_blk(binrespath, outpath, format_):
    old_rpath = f'aces_old.vromfs.bin_u_{format_}'
    old_path = os.path.join(binrespath, old_rpath)
    assert os.path.isdir(old_path)
    new_rpath = f'aces_new.vromfs.bin_u_{format_}'
    new_path = os.path.join(binrespath, new_rpath)
    assert os.path.isdir(new_path)

    unpacker = os.path.join(demo_prefix, 'blk_unpack_demo.py')
    os.system(f'python {unpacker} --format={format_} {new_path}')

    diff = os.path.join(outpath, f'{format_}.diff')
    os.system(f'diff -r {new_path} {old_path} > {diff}')
