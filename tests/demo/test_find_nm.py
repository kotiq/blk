import os
import pytest
from .blk_unpack_demo import names_path


@pytest.mark.parametrize(['rpath', 'nm_rpath'], [
    pytest.param('aces.vromfs.bin_u/gamedata/rumblepresets/rumblepresets.blk', 'aces.vromfs.bin_u/nm', id='slim'),
    pytest.param('game.vromfs.bin_u/gamedata/scenes/tank_compatibility_test_level.blk', None, id='fat'),
    pytest.param('launcher.vromfs.bin_u/laures/fonts.blk', None, id='bbf3'),
])
def test_find_nm(binrespath, rpath, nm_rpath):
    path = os.path.join(binrespath, rpath)
    if (maybe_nm_path := (names_path(path, 'nm'))) is None:
        assert maybe_nm_path == nm_rpath
    else:
        assert maybe_nm_path == os.path.join(binrespath, nm_rpath)
