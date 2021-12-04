from functools import partial
import itertools as itt
import os
from pathlib import Path
import typing as t


def is_blk(p: Path) -> bool:
    return p.suffix == '.blk'


def is_nm_or_blk(p: Path) -> bool:
    return is_blk(p) or p.name == 'nm'


def clean_tree(root: Path, pred: t.Callable[[Path], bool]):
    for p in root.rglob('*'):
        if pred(p):
            p.unlink()


def make_ignore(pred: t.Callable[[Path], bool]) -> t.Callable[[str, t.Iterable[str]], t.Iterable[str]]:
    def is_dir_or_p(parent: str, name: str) -> bool:
        full_name = os.path.join(parent, name)
        return os.path.isdir(full_name) or pred(Path(name))

    def ignore(parent: str, names: t.Iterable[str]) -> t.Iterable[str]:
        return set(itt.filterfalse(partial(is_dir_or_p, parent), names))

    return ignore


fat_dir_rpaths = [
    'game.vromfs.bin_u',
]

slim_dir_rpaths = [
    'aces.vromfs.bin_u',
]

bbf_dir_rpaths = [
    'aces.vromfs.bin_u',
]
