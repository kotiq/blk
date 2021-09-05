import os
import hashlib
import shlex
import subprocess
import pytest
import blk.binary as bin
import blk.json as jsn
from helpers import make_outpath

outpath = make_outpath(__name__)


def test_car_params(binrespath, outpath):
    diffpath = os.path.join(outpath, 'car_params.diff')
    if os.path.exists(diffpath):
        os.unlink(diffpath)
    old_json_path = os.path.join(binrespath, 'aces_old.vromfs.bin_u_json', 'config', 'car_params.blkx')
    new_nm_path = os.path.join(binrespath, 'aces_new.vromfs.bin_u_json', 'nm')
    new_blk_path = os.path.join(binrespath, 'aces_new.vromfs.bin_u_json', 'config', 'car_params.blk')
    new_json_path = os.path.join(outpath, 'car_params.json')
    with open(new_nm_path, 'rb') as istream:
        names = bin.compose_names(istream)

    with open(new_blk_path, 'rb') as istream:
        assert hashlib.md5(istream.read()).hexdigest() == 'c0d15459bb716798d2cdb2e2efb85390'
        istream.seek(0)
        root = bin.compose_slim(names, istream)

    with open(new_json_path, 'w', newline='', encoding='utf8') as ostream:
        jsn.serialize(root, ostream, jsn.JSON)

    try:
        subprocess.check_output(shlex.split(f'diff {old_json_path} {new_json_path}'), encoding='utf8')
    except subprocess.CalledProcessError as e:
        diff = e.stdout
        with open(diffpath, 'w') as ostream:
            ostream.write(diff)
        pytest.fail('diff')
