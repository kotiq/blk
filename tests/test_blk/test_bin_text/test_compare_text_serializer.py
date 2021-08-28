import io
import os
import time
import importlib
import pytest
import blk.binary as bin


@pytest.fixture(scope='module')
def wpcost(binrespath):
    char_path = os.path.join(binrespath, 'char.vromfs.bin_u')
    nm_path = os.path.join(char_path, 'nm')
    blk_path = os.path.join(char_path, 'config', 'wpcost.blk')
    with open(nm_path, 'rb') as istream:
        names = bin.compose_names(istream)
    with open(blk_path, 'rb') as istream:
        root = bin.compose_slim(names, istream)
    return root


def test_unpack_text(wpcost):
    ostream1 = io.StringIO()
    ostream2 = io.StringIO()
    n = 10

    serializer1 = importlib.import_module(f'blk.text.serializer')
    t0 = time.perf_counter()
    for _ in range(n):
        serializer1.serialize(wpcost, ostream1, serializer1.StrictDialect)
        ostream1.truncate(0)
    t1 = time.perf_counter()
    print(f'dt1 = {t1 - t0:.3f}')

    serializer2 = importlib.import_module(f'blk.text.serializer2')
    t0 = time.perf_counter()
    for _ in range(n):
        serializer2.serialize(wpcost, ostream2, serializer2.StrictDialect)
        ostream2.truncate(0)
    t1 = time.perf_counter()
    print(f'dt2 = {t1 - t0:.3f}')

    assert ostream1.getvalue() == ostream2.getvalue()
