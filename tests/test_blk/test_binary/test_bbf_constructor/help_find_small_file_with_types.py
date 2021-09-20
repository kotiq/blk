"""Поиск небольшого файла со всеми типами значений."""

from pathlib import Path
import heapq
import json
import pytest
from blk.types import *
from blk.binary.bbf_constructor import compose_bbf
from helpers import make_outpath, create_text
from . import bbf_paths

outpath = make_outpath(__name__)


def values(section: Section):
    for n, v in section.pairs():
        if isinstance(v, Section):
            yield v
            yield from values(v)
        else:
            yield v


def get_types(section: Section, classes: set) -> set:
    acc = set()
    for v in values(section):
        cls = v.__class__
        if (cls in classes) and (cls not in acc):
            acc.add(cls)
    return acc


@pytest.fixture(scope='module')
def typespath(outpath: Path):
    return outpath / 'types.json'


def test_collect(bbfrespath: Path, typespath: Path):
    m = {}
    for path in bbf_paths(bbfrespath):
        with open(path, 'rb') as istream:
            section = compose_bbf(istream)
            classes = {Bool, Str, Int, Long, Float, Int2, Int3, Color, Float2, Float3, Float4, Float12, Section}
            types_ = get_types(section, classes)
            size = path.stat().st_size
            rpath = str(path.relative_to(bbfrespath))
            cls_names = [cls.__name__ for cls in types_]
            m[rpath] = {'size': size, 'types': cls_names}

    with create_text(typespath) as ostream:
        json.dump(m, ostream, indent=2)


def with_bool(xs: set) -> bool:
    return 'Bool' in xs


def with_ints(xs: set) -> bool:
    return bool(xs & {'Int', 'Long'})


def with_scalars(xs: set) -> bool:
    return bool(xs & {'Str', 'Int', 'Long', 'Float'})


def with_vectors(xs: set) -> bool:
    return bool(xs & {'Int2', 'Int3', 'Color', 'Float2', 'Float3', 'Float4', 'Float12'})


def with_section(xs: set) -> bool:
    return 'Section' in xs


def test_get_small_files(typespath: Path):
    with open(typespath) as istream:
        m = json.load(istream)

    def f(item):
        _, st_m = item
        types_ = set(st_m['types'])
        return all(pred(types_) for pred in (with_bool, with_ints, with_scalars, with_vectors, with_section))

    m_ = dict(filter(f, m.items()))

    h = []
    for path, st_m in m_.items():
        size = st_m['size']
        types_ = st_m['types']
        heapq.heappush(h, (size, path, types_))

    for _ in range(5):
        item = heapq.heappop(h)
        print(item)



