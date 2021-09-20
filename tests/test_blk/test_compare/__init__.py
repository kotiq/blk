import os
from pathlib import Path
from functools import partial
import itertools as itt
import typing as t


def is_nm_blk(p: Path) -> bool:
    return p.name.endswith('.blk') or p.name == 'nm'


def clean_tree(root: Path, pred: t.Callable[[Path], bool]):
    for p in root.rglob('*'):
        if pred(p):
            p.unlink()


def is_dir_nm_blk(parent: str, name: str):
    full_name = os.path.join(parent, name)
    return os.path.isdir(full_name) or name.endswith('.blk') or name == 'nm'


def pass_dir_nm_blk(parent, names):
    return set(itt.filterfalse(partial(is_dir_nm_blk, parent), names))
