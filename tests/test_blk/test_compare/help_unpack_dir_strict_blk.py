import os
from pathlib import Path
from contextlib import contextmanager
import shutil
import multiprocessing as mp
import itertools as itt
from functools import partial
from datetime import datetime
import typing as t
import pytest
import blk.binary as bin
from blk.binary.constructor import Name
import blk.text as txt
from helpers import make_tmppath, create_text
from . import pass_dir_nm_blk, is_nm_blk, clean_tree


def is_fat_blk(path: Path) -> bool:
    if not path.is_file():
        return False
    if path.suffix != '.blk':
        return False
    if not path.stat().st_size:
        return False
    return True


def is_slim_blk(path: Path) -> bool:
    if not is_fat_blk(path):
        return False
    try:
        with open(path, 'rb') as file:
            bs = file.read(4)
            return not bs[0] and bs[1:4] != b'BBF\x03'
    except EnvironmentError:
        return False


time_fmt = '%d%m%y_%H%M%S'

tmppath = make_tmppath(__name__)


fat_dir_rpaths = [
    'game.vromfs.bin_u',
]

slim_dir_rpaths = [
    'aces.vromfs.bin_u',
]


# todo: разделить фикстуры
@pytest.fixture(scope='module')
def tmprespath(currespath: Path, tmppath: Path):
    dst_paths = []
    for dir_rpath in itt.chain(fat_dir_rpaths, slim_dir_rpaths):
        src = currespath / dir_rpath
        dst = tmppath / dir_rpath
        shutil.copytree(src, dst, ignore=pass_dir_nm_blk)
        dst_paths.append(dst)

    yield tmppath

    for dst in dst_paths:
        clean_tree(dst, is_nm_blk)


@pytest.mark.parametrize('dir_rpath', fat_dir_rpaths)
def test_unpack_fat_dir(tmprespath: Path, dir_rpath: str, request):
    dir_path = tmprespath / dir_rpath

    def process_file(path: Path, log):
        out_path = path.with_suffix('.blkx')
        try:
            with open(path, 'rb') as istream:
                root = bin.compose_fat_data(istream)
            with create_text(out_path) as ostream:
                txt.serialize(root, ostream, dialect=txt.StrictDialect)
            print(f'[ OK ] {path.relative_to(tmprespath)}', file=log)
        except Exception as e:
            print(f'[FAIL] {path.relative_to(tmprespath)}: {e}', file=log)

    def process_dir(path: Path, log):
        for p in path.iterdir():
            if p.is_dir():
                process_dir(p, log)
            elif is_fat_blk(p):
                process_file(p, log)

    utc = datetime.utcnow()
    log_name = '_'.join([utc.strftime(time_fmt), request.node.name, 'unpack.log'])
    log_path = dir_path / log_name
    with open(log_path, 'a') as log:
        process_dir(dir_path, log)


@pytest.mark.parametrize('dir_rpath', slim_dir_rpaths)
def test_unpack_slim_dir(tmprespath: Path, dir_rpath: str, request):
    dir_path = tmprespath / dir_rpath
    names_path = dir_path / 'nm'
    with open(names_path, 'rb') as istream:
        names = bin.compose_names_data(istream)

    def process_file(path: Path, log):
        out_path = path.with_suffix('.blkx')
        try:
            with open(path, 'rb') as istream:
                root = bin.compose_slim_data(names, istream)
            with create_text(out_path) as ostream:
                txt.serialize(root, ostream, txt.StrictDialect)
            print(f'[ OK ] {path.relative_to(tmprespath)}', file=log)
        except Exception as e:
            print(f'[FAIL] {path.relative_to(tmprespath)}: {e}', file=log)

    def process_dir(path: Path, log):
        for p in path.iterdir():
            if p.is_dir():
                process_dir(p, log)
            elif is_slim_blk(p):
                process_file(p, log)

    utc = datetime.utcnow()
    log_name = '_'.join([utc.strftime(time_fmt), request.node.name, 'unpack.log'])
    log_path = dir_path / log_name
    with open(log_path, 'a') as log:
        process_dir(dir_path, log)


def process_file_mp(path: Path, names: t.Sequence[Name], log, tmprespath: Path):
    out_path = path.with_suffix('.blkx')
    try:
        with open(path, 'rb') as istream:
            root = bin.compose_slim_data(names, istream)
        with create_text(out_path) as ostream:
            txt.serialize(root, ostream, dialect=txt.StrictDialect)
        ok_msg = f'[ OK ] {path.relative_to(tmprespath)}\n'
        os.write(log, ok_msg.encode('utf8'))
    except Exception as e:
        fail_msg = f'[FAIL] {path.relative_to(tmprespath)}: {e}\n'
        os.write(log, fail_msg.encode('utf8'))


def file_paths_r(path: Path):
    for p in path.iterdir():
        if p.is_dir():
            yield from file_paths_r(p)
        elif is_slim_blk(p):
            yield p


def process_dir_mp_pool(dir_path: Path, names: t.Sequence[Name], log, tmprespath: Path):
    file_paths = file_paths_r(dir_path)
    with mp.Pool(None) as pool:
        process_file = partial(process_file_mp, names=names, log=log, tmprespath=tmprespath)
        pool.map_async(process_file, file_paths)
        pool.close()
        pool.join()


@contextmanager
def os_open(*args, **kwargs):
    fd = os.open(*args, **kwargs)
    try:
        yield fd
    finally:
        os.close(fd)


@pytest.mark.parametrize('process_dir_mp', [
    process_dir_mp_pool,
])
@pytest.mark.parametrize('slim_dir_rpath', slim_dir_rpaths)
def test_unpack_slim_dir_mp(tmprespath: Path, slim_dir_rpath: str, request, process_dir_mp):
    slim_dir_path = tmprespath / slim_dir_rpath
    names_path = slim_dir_path / 'nm'
    with open(names_path, 'rb') as istream:
        names = bin.compose_names_data(istream)

    utc = datetime.utcnow()
    log_name = '_'.join([utc.strftime(time_fmt), request.node.name, 'unpack.log'])
    flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
    log_path = slim_dir_path / log_name
    with os_open(log_path, flags=flags, mode=0o644) as log:
        process_dir_mp(slim_dir_path, names, log, tmprespath)
