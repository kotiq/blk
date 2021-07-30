import os
from datetime import datetime
import pytest
import blk.binary as bin
import blk.text as txt


def is_fat_blk_entry(entry):
    if not entry.is_file():
        return False
    if not entry.name.endswith('.blk'):
        return False
    stat = entry.stat()
    if not stat.st_size:
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


@pytest.mark.parametrize('fat_dir_rpath', [
    'game.vromfs.bin_u',
])
def test_unpack_fat_dir(binrespath, fat_dir_rpath):
    fat_dir_path = os.path.join(binrespath, fat_dir_rpath)
    utc = datetime.utcnow()
    log = open(os.path.join(fat_dir_path, utc.strftime(time_fmt)+'_unpack.log'), 'a')

    def process_file(file_path):
        out_path = file_path + 'x'
        try:
            with open(file_path, 'rb') as istream:
                root = bin.compose_fat(istream)
            with open(out_path, 'w') as ostream:
                txt.serialize(root, ostream, dialect=txt.StrictDialect)
            print(f'[ OK ] {file_path!r}', file=log)
        except Exception as e:
            print(f'[FAIL] {file_path!r}: {e}', file=log)

    def process_dir(dir_path):
        for entry in os.scandir(dir_path):
            if entry.is_dir():
                process_dir(entry.path)
            elif is_fat_blk_entry(entry):
                process_file(entry.path)

    process_dir(fat_dir_path)


@pytest.mark.parametrize('slim_dir_rpath', [
    'aces.vromfs.bin_u',
    'char.vromfs.bin_u',
])
def test_unpack_slim_dir(binrespath, slim_dir_rpath):
    slim_dir_path = os.path.join(binrespath, slim_dir_rpath)
    names_path = os.path.join(slim_dir_path, 'nm')
    utc = datetime.utcnow()
    log = open(os.path.join(slim_dir_path, utc.strftime(time_fmt)+'_unpack.log'), 'a')

    try:
        with open(names_path, 'rb') as istream:
            names = bin.compose_names(istream)
    except EnvironmentError as e:
        pytest.fail(str(e))

    def process_file(file_path):
        out_path = file_path + 'x'
        try:
            with open(file_path, 'rb') as istream:
                root = bin.compose_slim(names, istream)
            with open(out_path, 'w') as ostream:
                txt.serialize(root, ostream, dialect=txt.StrictDialect)
            print(f'[ OK ] {file_path!r}', file=log)
        except Exception as e:
            print(f'[FAIL] {file_path!r}: {e}', file=log)

    def process_dir(dir_path):
        for entry in os.scandir(dir_path):
            if entry.is_dir():
                process_dir(entry.path)
            elif is_slim_blk_entry(entry):
                process_file(entry.path)

    process_dir(slim_dir_path)


















