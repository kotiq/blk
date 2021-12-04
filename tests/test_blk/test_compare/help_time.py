from pathlib import Path
import subprocess
from subprocess import DEVNULL
import platform
import time
import json
import pytest
import demo
from helpers import make_tmppath, make_outpath

demo_prefix = Path(demo.__path__[0])
tmppath = make_tmppath(__name__)
outpath = make_outpath(__name__)


dir_rpaths = [
    'aces.vromfs.bin_u',
    'aces.vromfs.bin_u_old',
]


@pytest.fixture(scope='module')
def time_log(outpath: Path):
    log_path = outpath / 'time.log'
    with open(log_path, 'a') as log:
        yield log


@pytest.fixture(scope='function')
def log_unpack_call(time_log):
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


@pytest.mark.skip("Перенести в wt-tools")
@pytest.mark.parametrize('rpath', dir_rpaths)
@pytest.mark.parametrize('runpacker', [
    'blk_unpack_demo.py',
    'blk_unpack_demo_mp.py',
])
def test_unpack(tmprespath: Path, runpacker: str, rpath: str, request, log_unpack_call: callable):
    path = tmprespath / rpath
    unpacker = demo_prefix / runpacker
    subprocess.run(['python', str(unpacker), str(path)], stdout=DEVNULL, stderr=DEVNULL)
    impl = platform.python_implementation()
    ver = platform.python_version()
    name = request.node.originalname
    log_unpack_call(impl=impl, ver=ver, name=name, unpacker=runpacker, path=rpath)
