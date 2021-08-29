import io
import os
import sys
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
    modules = []
    try:
        n = 10
        fmt = '{}: {} x dt = {:.3f}'
        print()

        names = ['serializer', 'serializer2']
        ostreams = [io.StringIO() for _ in names]

        for name, ostream in zip(names, ostreams):
            name = f'blk.text.{name}'
            maybe_module = sys.modules.get(name)
            module = importlib.import_module(name) if maybe_module is None else importlib.reload(maybe_module)
            modules.append(module)
            t0 = time.perf_counter()
            for _ in range(n):
                module.serialize(wpcost, ostream, module.StrictDialect)
                ostream.seek(0)
            t1 = time.perf_counter()
            print(fmt.format(name, n, t1 - t0))

        head, *tail = ostreams
        for i, other in enumerate(tail, 1):
            assert head.getvalue() == other.getvalue(), names[i]
    finally:
        if len(modules) > 1:
            importlib.reload(modules[0])
