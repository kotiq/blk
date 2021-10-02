from pathlib import Path
import io
import typing as t
from functools import partial
import pytest
from helpers import make_outpath, create_text
from blk.binary.constructor import (compose_fat_data, serialize_fat_data, compose_slim_data, Names, InvNames, serialize_slim_data)
import blk.text as txt

serialize_text = partial(txt.serialize, dialect=txt.StrictDialect)
outpath = make_outpath(__name__)


@pytest.fixture()
def iostream():
    return io.BytesIO()


@pytest.mark.parametrize('rpath', [
    pytest.param('game.vromfs.bin_u/gamedata/scenes/tank_compatibility_test_level.blk',  id='fat file'),
    pytest.param('game.vromfs.bin_u/config/_net.blk', id='fat_s file'),
])
def test_compose_fat(currespath: Path, rpath: str, outpath: Path):
    ipath = currespath / rpath
    opath = outpath / Path(rpath).with_suffix('.blkx').name

    with open(ipath, 'rb') as istream:
        root = compose_fat_data(istream)

    with create_text(opath) as ostream:
        serialize_text(root, ostream)


@pytest.mark.parametrize(['strings_in_names', 'rpath'], [
    pytest.param(False, 'game.vromfs.bin_u/gamedata/scenes/tank_compatibility_test_level.blk', id='fat file'),
    pytest.param(True, 'game.vromfs.bin_u/config/_net.blk', id='fat_s file')
])
def test_serialize_fat(strings_in_names: bool, currespath: Path, rpath: str, outpath: Path, iostream: t.BinaryIO):
    ipath = currespath / rpath
    opath_text = outpath / Path(rpath).with_suffix('.blkx').name

    with open(ipath, 'rb') as istream:
        root = compose_fat_data(istream)

    with create_text(opath_text) as ostream:
        serialize_text(root, ostream)

    serialize_fat_data(root, iostream, strings_in_names)

    opath_bin = outpath / Path(rpath).with_suffix('.bin').name
    iostream.seek(0)
    opath_bin.write_bytes(iostream.read())

    iostream.seek(0)
    assert root == compose_fat_data(iostream)


def test_compose_slim(currespath: Path, outpath: Path):
    nm_rpath = currespath / 'aces.vromfs.bin_u/nm'
    rpath = 'aces.vromfs.bin_u/settings.blk'
    nm_ipath = currespath / nm_rpath
    ipath = currespath / rpath
    opath = outpath / Path(rpath).with_suffix('.blkx').name

    with open(nm_ipath, 'rb') as istream:
        names = Names.parse_stream(istream)

    with open(ipath, 'rb') as istream:
        root = compose_slim_data(names, istream)

    with create_text(opath) as ostream:
        serialize_text(root, ostream)


def test_serialize_slim(currespath: Path, outpath: Path, iostream: t.BinaryIO):
    nm_rpath = currespath / 'aces.vromfs.bin_u/nm'
    rpath = 'aces.vromfs.bin_u/settings.blk'
    nm_ipath = currespath / nm_rpath
    ipath = currespath / rpath
    opath = outpath / Path(rpath).with_suffix('.bin').name

    with open(nm_ipath, 'rb') as istream:
        names = Names.parse_stream(istream)

    with open(ipath, 'rb') as istream:
        root = compose_slim_data(names, istream)

    inv_names = InvNames(names)
    len_before = len(inv_names)
    serialize_slim_data(root, inv_names, iostream)

    iostream.seek(0)
    opath.write_bytes(iostream.read())

    iostream.seek(0)
    assert root == compose_slim_data(names, iostream)
    assert len_before == len(inv_names)
