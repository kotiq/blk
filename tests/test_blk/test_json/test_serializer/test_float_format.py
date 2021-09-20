from pathlib import Path
import hashlib
import shlex
import subprocess
import pytest
import blk_unpack as bbf3
import blk.binary as bin
import blk.json as jsn
from helpers import make_outpath, create_text

outpath = make_outpath(__name__)
out_type = jsn.JSON


@pytest.fixture(scope='module')
def old_blk_path(currespath: Path):
    return currespath / 'aces_old.vromfs.bin_u_json' / 'config' / 'car_params.blk'


@pytest.fixture(scope='module')
def new_blk_path(currespath: Path):
    return currespath / 'aces_new.vromfs.bin_u_json' / 'config' / 'car_params.blk'


@pytest.fixture(scope='module')
def old_json_path(old_blk_path: Path, outpath: Path):
    bs = old_blk_path.read_bytes()
    bbf3_parser = bbf3.BLK(bs)
    ss = bbf3_parser.unpack(out_type)

    out_json_path_ = outpath / f'old_{old_blk_path.name}.json'
    with create_text(out_json_path_) as ostream:
        ostream.write(ss)
    return out_json_path_


@pytest.fixture(scope='module')
def new_nm_path(currespath: Path):
    return currespath / 'aces_new.vromfs.bin_u_json' / 'nm'


@pytest.fixture(scope='module')
def new_json_path(new_blk_path: Path, new_nm_path: Path, outpath: Path):
    with open(new_nm_path, 'rb') as istream:
        names = bin.compose_names(istream)

    assert hashlib.md5(new_blk_path.read_bytes()).hexdigest() == 'c0d15459bb716798d2cdb2e2efb85390'

    with open(new_blk_path, 'rb') as istream:
        root = bin.compose_slim(names, istream)

    new_json_path_ = outpath / f'new_{new_blk_path.name}.json'
    with create_text(new_json_path_) as ostream:
        jsn.serialize(root, ostream, out_type)

    return new_json_path_


@pytest.fixture(scope='module')
def diffpath(new_blk_path: Path, outpath: Path):
    diffpath_ = outpath / f'{new_blk_path.name}.diff'
    if diffpath_.exists():
        diffpath_.unlink()
    return diffpath_


def test_car_params(old_json_path: Path, new_json_path: Path, diffpath: Path):
    try:
        subprocess.check_output(shlex.split(f'diff {old_json_path} {new_json_path}'), encoding='utf8')
    except subprocess.CalledProcessError as e:
        diff = e.stdout
        with create_text(diffpath) as ostream:
            ostream.write(diff)
        pytest.fail('diff')
