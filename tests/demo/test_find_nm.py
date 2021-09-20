import os
from pathlib import Path
import typing as t
import pytest
from .blk_unpack_demo import names_path


@pytest.mark.parametrize(['rpath', 'nm_rpath'], [
    pytest.param('aces.vromfs.bin_u/gamedata/rumblepresets/rumblepresets.blk', 'aces.vromfs.bin_u/nm', id='slim'),
    pytest.param('game.vromfs.bin_u/gamedata/scenes/tank_compatibility_test_level.blk', None, id='fat'),
    pytest.param('launcher.vromfs.bin_u/laures/fonts.blk', None, id='bbf3'),
])
def test_find_nm(currespath: Path, rpath: str, nm_rpath: t.Optional[str]):
    path = currespath / rpath
    maybe_nm_path = (names_path(path, 'nm'))
    if maybe_nm_path is None:
        assert maybe_nm_path == nm_rpath
    else:
        assert maybe_nm_path == currespath / nm_rpath
