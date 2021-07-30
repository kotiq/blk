import os
from io import BytesIO
from functools import partial
import pytest
from blk.binary.constructor import (compose_fat, serialize_fat, serialize_fat_s,
                                    compose_slim, Names, serialize_slim)
from blk.text.serializer import serialize, DefaultDialect, StrictDialect

serialize_text = partial(serialize, dialect=StrictDialect)


outdir_rpath = os.path.join('tests', *__name__.split('.'))


@pytest.mark.parametrize('rpath', [
    pytest.param('game.vromfs.bin_u/gamedata/scenes/tank_compatibility_test_level.blk',  id='fat file'),
    pytest.param('game.vromfs.bin_u/config/_net.blk', id='fat_s file'),
])
def test_compose_fat(binrespath, rpath, buildpath):
    filename = os.path.join(binrespath, rpath)
    with open(filename, 'rb') as istream:
        root = compose_fat(istream)

    outdir_path = os.path.join(buildpath, outdir_rpath)
    os.makedirs(outdir_path, exist_ok=True)
    out_path = os.path.join(outdir_path, os.path.basename(rpath))

    with open(out_path + '.txt', 'w') as ostream:
        serialize_text(root, ostream)


@pytest.mark.parametrize(['serialize_bin', 'rpath'], [
    pytest.param(serialize_fat, 'game.vromfs.bin_u/gamedata/scenes/tank_compatibility_test_level.blk', id='fat file'),
    pytest.param(serialize_fat_s, 'game.vromfs.bin_u/config/_net.blk', id='fat_s file')
])
def test_serialize_fat(serialize_bin, binrespath, rpath, buildpath):
    filename = os.path.join(binrespath, rpath)
    with open(filename, 'rb') as istream:
        root = compose_fat(istream)

    outdir_path = os.path.join(buildpath, outdir_rpath)
    os.makedirs(outdir_path, exist_ok=True)
    out_path = os.path.join(outdir_path, os.path.basename(rpath))

    iostream = BytesIO()
    serialize_bin(root, iostream)

    with open(out_path + '.bin', 'wb') as ostream:
        ostream.write(iostream.getvalue())

    iostream.seek(0)
    assert root == compose_fat(iostream)


def test_compose_slim(binrespath, buildpath):
    nm_rpath = '/media/games/kotiq/resources/aces.vromfs.bin_u/nm'
    rpath = 'aces.vromfs.bin_u/settings.blk'

    nm_filename = os.path.join(binrespath, nm_rpath)
    with open(nm_filename, 'rb') as istream:
        names = Names.parse_stream(istream)

    filename = os.path.join(binrespath, rpath)
    with open(filename, 'rb') as istream:
        root = compose_slim(names, istream)

    outdir_path = os.path.join(buildpath, outdir_rpath)
    os.makedirs(outdir_path, exist_ok=True)
    out_path = os.path.join(outdir_path, os.path.basename(rpath))

    with open(out_path + '.txt', 'w') as ostream:
        serialize_text(root, ostream)


def test_serialize_slim(binrespath, buildpath):
    nm_rpath = '/media/games/kotiq/resources/aces.vromfs.bin_u/nm'
    rpath = 'aces.vromfs.bin_u/settings.blk'

    nm_filename = os.path.join(binrespath, nm_rpath)
    with open(nm_filename, 'rb') as istream:
        names = Names.parse_stream(istream)

    filename = os.path.join(binrespath, rpath)
    with open(filename, 'rb') as istream:
        root = compose_slim(names, istream)

    outdir_path = os.path.join(buildpath, outdir_rpath)
    os.makedirs(outdir_path, exist_ok=True)
    out_path = os.path.join(outdir_path, os.path.basename(rpath))

    names_map = {name: i for i, name in enumerate(names)}
    len_before = len(names_map)

    iostream = BytesIO()
    serialize_slim(root, names_map, iostream)

    with open(out_path + '.bin', 'wb') as ostream:
        ostream.write(iostream.getvalue())

    iostream.seek(0)
    assert root == compose_slim(names, iostream)
    assert len_before == len(names_map)
