import os
from pathlib import Path
import shutil
import typing as t
import pytest
from helpers import make_outpath, make_tmppath
import demo
from . import pass_dir_nm_blk, is_nm_blk, clean_tree

demo_prefix = Path(demo.__path__[0])
outpath = make_outpath(__name__)
tmppath = make_tmppath(__name__)


class Paths(t.NamedTuple):
    old: Path
    new: Path
    fmt: str


@pytest.fixture(scope='module', params=['strict_blk', 'json', 'json_2'])
def paths(currespath: Path, outpath: Path, tmppath: Path, request):
    fmt = request.param

    old_ = f'aces_old.vromfs.bin_u_{fmt}'
    old_src = currespath / old_
    old_dst = tmppath / old_
    shutil.copytree(old_src, old_dst, ignore=pass_dir_nm_blk)
    old_log = outpath / f'bbf_{fmt}.log'
    os.system(f'python -m blk_unpack --format={fmt} {old_dst} > {old_log}')

    new_ = f'aces_new.vromfs.bin_u_{fmt}'
    new_src = currespath / new_
    new_dst = tmppath / new_
    shutil.copytree(new_src, new_dst, ignore=pass_dir_nm_blk)
    new_log = outpath / f'cur_{fmt}.log'
    unpacker = demo_prefix / 'blk_unpack_demo_mp.py'
    os.system(f'python {unpacker} --format={fmt} {new_dst} > {new_log}')

    yield Paths(old_dst, new_dst, fmt)

    clean_tree(old_dst, is_nm_blk)
    clean_tree(new_dst, is_nm_blk)


def test_unpack(paths: Paths, outpath: Path):
    diff = outpath / f'{paths.fmt}.diff'
    os.system(f"diff -r -x '*.blk' -x '*.dict' {paths.new} {paths.old} > {diff}")
