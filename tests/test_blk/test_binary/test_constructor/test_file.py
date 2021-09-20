# import os
from pathlib import Path
from collections import OrderedDict
from io import BytesIO
from functools import partial
import pytest
from helpers import make_outpath, create_text
from blk.binary.constructor import (compose_fat, serialize_fat, serialize_fat_s,
                                    compose_slim, Names, serialize_slim)
import blk.text as txt

serialize_text = partial(txt.serialize, dialect=txt.StrictDialect)
outpath = make_outpath(__name__)


@pytest.mark.parametrize('rpath', [
    pytest.param('game.vromfs.bin_u/gamedata/scenes/tank_compatibility_test_level.blk',  id='fat file'),
    pytest.param('game.vromfs.bin_u/config/_net.blk', id='fat_s file'),
])
def test_compose_fat(currespath: Path, rpath: str, outpath: Path):
    ipath = currespath / rpath
    opath = outpath / Path(rpath).with_suffix('.blkx').name

    with open(ipath, 'rb') as istream:
        root = compose_fat(istream)

    with create_text(opath) as ostream:
        serialize_text(root, ostream)


@pytest.mark.parametrize(['serialize_bin', 'rpath'], [
    pytest.param(serialize_fat, 'game.vromfs.bin_u/gamedata/scenes/tank_compatibility_test_level.blk', id='fat file'),
    pytest.param(serialize_fat_s, 'game.vromfs.bin_u/config/_net.blk', id='fat_s file')
])
def test_serialize_fat(serialize_bin: callable, currespath: Path, rpath: str, outpath: Path):
    ipath = currespath / rpath
    opath_text = outpath / Path(rpath).with_suffix('.blkx').name

    with open(ipath, 'rb') as istream:
        root = compose_fat(istream)

    with create_text(opath_text) as ostream:
        serialize_text(root, ostream)

    iostream = BytesIO()
    serialize_bin(root, iostream)

    opath_bin = outpath / Path(rpath).with_suffix('.bin').name
    with open(opath_bin, 'wb') as ostream:
        ostream.write(iostream.getvalue())

    iostream.seek(0)
    assert root == compose_fat(iostream)


def test_compose_slim(currespath: Path, outpath: Path):
    nm_rpath = currespath / 'aces.vromfs.bin_u/nm'
    rpath = 'aces.vromfs.bin_u/settings.blk'
    nm_ipath = currespath / nm_rpath
    ipath = currespath / rpath
    opath = outpath / Path(rpath).with_suffix('.blkx').name

    with open(nm_ipath, 'rb') as istream:
        names = Names.parse_stream(istream)

    with open(ipath, 'rb') as istream:
        root = compose_slim(names, istream)

    with create_text(opath) as ostream:
        serialize_text(root, ostream)


def test_serialize_slim(currespath: Path, outpath: Path):
    nm_rpath = currespath / 'aces.vromfs.bin_u/nm'
    rpath = 'aces.vromfs.bin_u/settings.blk'
    nm_ipath = currespath / nm_rpath
    ipath = currespath / rpath
    opath = outpath / Path(rpath).with_suffix('.bin').name

    with open(nm_ipath, 'rb') as istream:
        names = Names.parse_stream(istream)

    with open(ipath, 'rb') as istream:
        root = compose_slim(names, istream)

    names_map = OrderedDict((name, i) for i, name in enumerate(names))
    len_before = len(names_map)

    iostream = BytesIO()
    serialize_slim(root, names_map, iostream)

    with open(opath, 'wb') as ostream:
        ostream.write(iostream.getvalue())

    iostream.seek(0)
    assert root == compose_slim(names, iostream)
    assert len_before == len(names_map)
