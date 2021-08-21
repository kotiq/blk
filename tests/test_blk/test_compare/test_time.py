import os
import subprocess
from subprocess import DEVNULL
import platform
import time
import json
from shutil import copytree
from functools import partial
import itertools as itt
import pytest
import demo
from helpers import make_tmppath, make_outpath

demo_prefix = demo.__path__[0]
tmppath = make_tmppath(__name__)
outpath = make_outpath(__name__)


dir_rpaths = [
    'aces.vromfs.bin_u',
    'aces.vromfs.bin_u_old',
]


def is_dir_nm_blk(parent, name):
    full_name = os.path.join(parent, name)
    return os.path.isdir(full_name) or name.endswith('.blk') or name == 'nm'


def pass_dir_nm_blk(parent, names):
    return set(itt.filterfalse(partial(is_dir_nm_blk, parent), names))


@pytest.fixture(scope='module')
def tmprespath(binrespath, tmppath):
    for dir_rpath in dir_rpaths:
        src = os.path.join(binrespath, dir_rpath)
        dst = os.path.join(tmppath, dir_rpath)
        copytree(src, dst, ignore=pass_dir_nm_blk)
    return tmppath


@pytest.fixture(scope='module')
def time_log(outpath):
    with open(os.path.join(outpath, 'time.log'), 'a') as log:
        yield log


@pytest.fixture(scope='function')
def log_unpack_call(time_log,):
    ns = dict()

    def init(**kwargs):
        ns.update(**kwargs)

    start = time.perf_counter()
    yield init
    stop = time.perf_counter()
    ns['call'] = round(stop - start, 3)
    json.dump(ns, time_log)
    time_log.write('\n')
    time_log.flush()


@pytest.mark.parametrize('rpath', dir_rpaths)
@pytest.mark.parametrize('runpacker', [
    'blk_unpack_demo.py',
    'blk_unpack_demo_mp.py',
])
def test_unpack(tmprespath, runpacker, rpath, request, log_unpack_call):
    path = os.path.join(tmprespath, rpath)
    unpacker = os.path.join(demo_prefix, runpacker)
    subprocess.run(['python', unpacker, path], stdout=DEVNULL, stderr=DEVNULL)
    impl = platform.python_implementation()
    ver = platform.python_version()
    name = request.node.originalname
    log_unpack_call(impl=impl, ver=ver, name=name, unpacker=runpacker, path=rpath)
