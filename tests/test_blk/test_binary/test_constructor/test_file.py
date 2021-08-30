import os
from collections import OrderedDict
from io import BytesIO
from functools import partial
import pytest
from helpers import make_outpath
from blk.binary.constructor import (compose_fat, serialize_fat, serialize_fat_s,
                                    compose_slim, Names, serialize_slim)
import blk.text as txt

serialize_text = partial(txt.serialize, dialect=txt.StrictDialect)
outpath = make_outpath(__name__)


@pytest.mark.parametrize('rpath', [
    pytest.param('game.vromfs.bin_u/gamedata/scenes/tank_compatibility_test_level.blk',  id='fat file'),
    pytest.param('game.vromfs.bin_u/config/_net.blk', id='fat_s file'),
])
def test_compose_fat(binrespath, rpath, outpath):
    ipath = os.path.join(binrespath, rpath)
    opath = os.path.join(outpath, os.path.basename(rpath))

    with open(ipath, 'rb') as istream:
        root = compose_fat(istream)

    with open(opath + '.txt', 'w') as ostream:
        serialize_text(root, ostream)


@pytest.mark.parametrize(['serialize_bin', 'rpath'], [
    pytest.param(serialize_fat, 'game.vromfs.bin_u/gamedata/scenes/tank_compatibility_test_level.blk', id='fat file'),
    pytest.param(serialize_fat_s, 'game.vromfs.bin_u/config/_net.blk', id='fat_s file')
])
def test_serialize_fat(serialize_bin, binrespath, rpath, outpath):
    ipath = os.path.join(binrespath, rpath)
    opath = os.path.join(outpath, os.path.basename(rpath))

    with open(ipath, 'rb') as istream:
        root = compose_fat(istream)

    with open(opath + '.txt', 'w') as ostream:
        serialize_text(root, ostream)

    iostream = BytesIO()
    serialize_bin(root, iostream)

    with open(opath + '.bin', 'wb') as ostream:
        ostream.write(iostream.getvalue())

    iostream.seek(0)
    assert root == compose_fat(iostream)


def test_compose_slim(binrespath, outpath):
    nm_rpath = '/media/games/kotiq/resources/aces.vromfs.bin_u/nm'
    rpath = 'aces.vromfs.bin_u/settings.blk'
    nm_ipath = os.path.join(binrespath, nm_rpath)
    ipath = os.path.join(binrespath, rpath)
    opath = os.path.join(outpath, os.path.basename(rpath))

    with open(nm_ipath, 'rb') as istream:
        names = Names.parse_stream(istream)

    with open(ipath, 'rb') as istream:
        root = compose_slim(names, istream)

    with open(opath + '.txt', 'w') as ostream:
        serialize_text(root, ostream)


def test_serialize_slim(binrespath, outpath):
    nm_rpath = '/media/games/kotiq/resources/aces.vromfs.bin_u/nm'
    rpath = 'aces.vromfs.bin_u/settings.blk'
    nm_ipath = os.path.join(binrespath, nm_rpath)
    ipath = os.path.join(binrespath, rpath)
    opath = os.path.join(outpath, os.path.basename(rpath))

    with open(nm_ipath, 'rb') as istream:
        names = Names.parse_stream(istream)

    with open(ipath, 'rb') as istream:
        root = compose_slim(names, istream)

    names_map = OrderedDict((name, i) for i, name in enumerate(names))
    len_before = len(names_map)

    iostream = BytesIO()
    serialize_slim(root, names_map, iostream)

    with open(opath + '.bin', 'wb') as ostream:
        ostream.write(iostream.getvalue())

    iostream.seek(0)
    assert root == compose_slim(names, iostream)
    assert len_before == len(names_map)
