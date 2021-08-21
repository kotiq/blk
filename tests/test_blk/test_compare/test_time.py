import os
import pytest
import demo

demo_prefix = demo.__path__[0]


@pytest.mark.parametrize('rpath', [
    'aces.vromfs.bin_u',
    'aces.vromfs.bin_u_old',
])
@pytest.mark.parametrize('runpacker', [
    'blk_unpack_demo.py',
    'blk_unpack_demo_mp.py',
])
def test_unpack(binrespath, runpacker, rpath):
    path = os.path.join(binrespath, rpath)
    unpacker = os.path.join(demo_prefix, runpacker)
    os.system(f'python {unpacker} {path} > /dev/null')
