from pathlib import Path
from .blk_unpack_demo import is_text


def test_is_text(cdkpath: Path):
    for p in cdkpath.rglob('*.blk'):
        with open(p, 'rb') as istream:
            assert is_text(istream)
