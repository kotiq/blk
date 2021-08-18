import os
import json
from contextlib import contextmanager
from shutil import copytree
import multiprocessing as mp
import itertools as itt
from functools import partial
from datetime import datetime
import pytest
import blk.binary as bin
import blk.text as txt
import blk.json as jsn
from helpers import make_tmppath, create_text


def is_fat_blk_entry(entry):
    if not entry.is_file():
        return False
    if not entry.name.endswith('.blk'):
        return False
    stat_ = entry.stat()
    if not stat_.st_size:
        return False
    return True


def is_slim_blk_entry(entry):
    if not is_fat_blk_entry(entry):
        return False
    try:
        with open(entry.path, 'rb') as file:
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
    # 'aces.vromfs.bin_u',
    'char.vromfs.bin_u',
]


def is_dir_nm_blk(parent, name):
    full_name = os.path.join(parent, name)
    return os.path.isdir(full_name) or name.endswith('.blk') or name == 'nm'


def pass_dir_nm_blk(parent, names):
    return set(itt.filterfalse(partial(is_dir_nm_blk, parent), names))


@pytest.fixture(scope='module')
def tmprespath(binrespath, tmppath):
    for dir_rpath in itt.chain(fat_dir_rpaths, slim_dir_rpaths):
        src = os.path.join(binrespath, dir_rpath)
        dst = os.path.join(tmppath, dir_rpath)
        copytree(src, dst, ignore=pass_dir_nm_blk)
    return tmppath


@pytest.mark.parametrize('dir_rpath', fat_dir_rpaths)
def test_unpack_fat_dir(tmprespath, dir_rpath, request):
    dir_path = os.path.join(tmprespath, dir_rpath)

    def process_file(path, log):
        out_path = path + 'x'
        try:
            with open(path, 'rb') as istream:
                root = bin.compose_fat(istream)
            with create_text(out_path) as ostream:
                txt.serialize(root, ostream, dialect=txt.StrictDialect)
            print(f'[ OK ] {os.path.relpath(path, tmprespath)!r}', file=log)
        except Exception as e:
            print(f'[FAIL] {os.path.relpath(path, tmprespath)!r}: {e}', file=log)

    def process_dir(path, log):
        for entry in os.scandir(path):
            if entry.is_dir():
                process_dir(entry.path, log)
            elif is_fat_blk_entry(entry):
                process_file(entry.path, log)

    utc = datetime.utcnow()
    log_name = '_'.join([utc.strftime(time_fmt), request.node.name, 'unpack.log'])
    with open(os.path.join(dir_path, log_name), 'a') as log:
        process_dir(dir_path, log)


@pytest.mark.parametrize(['serializer', 'ext'], [
    pytest.param(lambda root, ostream: txt.serialize(root, ostream, txt.StrictDialect), '.blkx', id='strict_blk'),
    pytest.param(lambda root, ostream: json.dump(root, ostream), '.identity.json', id='json_as_is'),
    pytest.param(lambda root, ostream: jsn.serialize(root, ostream, jsn.JSON), '.default.json', id='json'),
    pytest.param(lambda root, ostream: jsn.serialize(root, ostream, jsn.JSON_2), '.alternate.json', id='json_2'),
])
@pytest.mark.parametrize('dir_rpath', slim_dir_rpaths)
def test_unpack_slim_dir(tmprespath, dir_rpath, request, serializer, ext):
    dir_path = os.path.join(tmprespath, dir_rpath)
    names_path = os.path.join(dir_path, 'nm')
    try:
        with open(names_path, 'rb') as istream:
            names = bin.compose_names(istream)
    except EnvironmentError as e:
        pytest.fail(str(e))

    def process_file(path, log):
        out_path = os.path.splitext(path)[0] + ext
        try:
            with open(path, 'rb') as istream:
                root = bin.compose_slim(names, istream)
            with create_text(out_path) as ostream:
                serializer(root, ostream)
            print(f'[ OK ] {os.path.relpath(path, tmprespath)!r}', file=log)
        except Exception as e:
            print(f'[FAIL] {os.path.relpath(path, tmprespath)!r}: {e}', file=log)

    def process_dir(path, log):
        for entry in os.scandir(path):
            if entry.is_dir():
                process_dir(entry.path, log)
            elif is_slim_blk_entry(entry):
                process_file(entry.path, log)

    utc = datetime.utcnow()
    log_name = '_'.join([utc.strftime(time_fmt), request.node.name, 'unpack.log'])
    with open(os.path.join(dir_path, log_name), 'a') as log:
        process_dir(dir_path, log)


def process_file_mp(file_path, names, log, tmprespath):
    out_path = file_path + 'x'
    try:
        with open(file_path, 'rb') as istream:
            root = bin.compose_slim(names, istream)
        with create_text(out_path) as ostream:
            txt.serialize(root, ostream, dialect=txt.StrictDialect)
        ok_msg = f'[ OK ] {os.path.relpath(file_path, tmprespath)!r}\n'
        os.write(log, ok_msg.encode('utf8'))
    except Exception as e:
        fail_msg = f'[FAIL] {os.path.relpath(file_path, tmprespath)!r}: {e}\n'
        os.write(log, fail_msg.encode('utf8'))


def process_dir_mp(dir_path, names, log, tmprespath, pool):
    dir_paths = []
    file_paths = []
    for entry in os.scandir(dir_path):
        if entry.is_dir():
            dir_paths.append(entry.path)
        elif is_slim_blk_entry(entry):
            file_paths.append(entry.path)

    for dir_path in dir_paths:
        process_dir_mp(dir_path, names, log, tmprespath, pool)

    pool.map(partial(process_file_mp, names=names, log=log, tmprespath=tmprespath), file_paths)


@contextmanager
def os_open(*args, **kwargs):
    fd = os.open(*args, **kwargs)
    try:
        yield fd
    finally:
        os.close(fd)


@pytest.mark.parametrize('slim_dir_rpath', slim_dir_rpaths)
def test_unpack_slim_dir_mp(tmprespath, slim_dir_rpath, request):
    slim_dir_path = os.path.join(tmprespath, slim_dir_rpath)
    names_path = os.path.join(slim_dir_path, 'nm')
    try:
        with open(names_path, 'rb') as istream:
            names = bin.compose_names(istream)
    except EnvironmentError as e:
        pytest.fail(str(e))

    utc = datetime.utcnow()
    log_name = '_'.join([utc.strftime(time_fmt), request.node.name, 'unpack.log'])
    flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
    with os_open(os.path.join(slim_dir_path, log_name), flags=flags, mode=0o644) as log:
        with mp.Pool(None) as pool:
            process_dir_mp(slim_dir_path, names, log, tmprespath, pool)
            pool.close()
            pool.join()
