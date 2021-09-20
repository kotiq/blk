import os
from pathlib import Path
import pytest
from blk.binary.constructor import Names


@pytest.mark.parametrize('compile_', [
    False,
    True,
])
@pytest.mark.parametrize('slim_dir_rpath', [
    'aces.vromfs.bin_u',
    'char.vromfs.bin_u',
])
def test_compose_names(currespath: Path, slim_dir_rpath: str, compile_: bool):
    con = Names if not compile_ else Names.compile()
    names_path = currespath / slim_dir_rpath / 'nm'
    with open(names_path, 'rb') as istream:
        names = con.parse_stream(istream)
