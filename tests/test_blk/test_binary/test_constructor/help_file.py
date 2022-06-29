from pathlib import Path
from functools import partial
import pytest
from pytest import param as _
from helpers import create_text, make_outpath
from blk.binary.constructor import (InvNames, Names, compose_partial_fat, compose_partial_slim, serialize_fat_data,
                                    serialize_slim_data)
import blk.text as txt

serialize_text = partial(txt.serialize, dialect=txt.StrictDialect)
outpath = make_outpath(__name__)


@pytest.mark.parametrize('rpath', [
    _('game.vromfs.bin_u/gamedata/scenes/tank_compatibility_test_level.blk',  id='fat file'),
    _('game.vromfs.bin_u/config/_net.blk', id='fat_s file'),
])
def test_compose_fat(currespath, rpath, outpath):
    ipath = currespath / rpath
    opath = outpath / Path(rpath).with_suffix('.blkx').name

    with open(ipath, 'rb') as istream:
        root = compose_partial_fat(istream)

    with create_text(opath) as ostream:
        serialize_text(root, ostream)


@pytest.mark.parametrize(['strings_in_names', 'rpath'], [
    _(False, 'game.vromfs.bin_u/gamedata/scenes/tank_compatibility_test_level.blk', id='fat file'),
    _(True, 'game.vromfs.bin_u/config/_net.blk', id='fat_s file')
])
def test_serialize_fat(strings_in_names, currespath, rpath, outpath, iostream):
    ipath = currespath / rpath
    opath_text = outpath / Path(rpath).with_suffix('.blkx').name

    with open(ipath, 'rb') as istream:
        root = compose_partial_fat(istream)

    with create_text(opath_text) as ostream:
        serialize_text(root, ostream)

    serialize_fat_data(root, iostream, strings_in_names)

    opath_bin = outpath / Path(rpath).with_suffix('.bin').name
    iostream.seek(0)
    opath_bin.write_bytes(iostream.read())

    iostream.seek(0)
    assert root == compose_partial_fat(iostream)


def test_compose_slim(currespath, outpath):
    nm_rpath = currespath / 'aces.vromfs.bin_u/nm'
    rpath = 'aces.vromfs.bin_u/settings.blk'
    nm_ipath = currespath / nm_rpath
    ipath = currespath / rpath
    opath = outpath / Path(rpath).with_suffix('.blkx').name

    with open(nm_ipath, 'rb') as istream:
        names = Names.parse_stream(istream)

    with open(ipath, 'rb') as istream:
        root = compose_partial_slim(names, istream)

    with create_text(opath) as ostream:
        serialize_text(root, ostream)


def test_serialize_slim(currespath, outpath, iostream):
    nm_rpath = currespath / 'aces.vromfs.bin_u/nm'
    rpath = 'aces.vromfs.bin_u/settings.blk'
    nm_ipath = currespath / nm_rpath
    ipath = currespath / rpath
    opath = outpath / Path(rpath).with_suffix('.bin').name

    with open(nm_ipath, 'rb') as istream:
        names = Names.parse_stream(istream)

    with open(ipath, 'rb') as istream:
        root = compose_partial_slim(names, istream)

    inv_names = InvNames(names)
    len_before = len(inv_names)
    serialize_slim_data(root, inv_names, iostream)

    iostream.seek(0)
    opath.write_bytes(iostream.read())

    iostream.seek(0)
    assert root == compose_partial_slim(names, iostream)
    assert len_before == len(inv_names)
