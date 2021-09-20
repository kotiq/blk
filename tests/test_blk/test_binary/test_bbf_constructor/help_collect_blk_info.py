from pathlib import Path
import json
import heapq
from collections import defaultdict, OrderedDict
import pytest
from helpers import make_outpath, create_text
from . import bbf_paths

outpath = make_outpath(__name__)


@pytest.fixture(scope='module')
def blk_version_summary_path(outpath: Path):
    return outpath / 'blk_version_summary.json'


@pytest.fixture(scope='module')
def blk_names_summary_path(outpath: Path):
    return outpath / 'blk_names_summary.json'


def test_collect_blk_versions(bbfrespath: Path, blk_version_summary_path: Path):
    m = defaultdict(list)
    for path in bbf_paths(bbfrespath):
        with open(path, 'rb') as istream:
            istream.seek(4)
            hi = int.from_bytes(istream.read(2), 'little')
            lo = int.from_bytes(istream.read(2), 'little')
            rpath = str(path.relative_to(bbfrespath))
            m[hi, lo].append(rpath)
    sm = OrderedDict((f'{k[0]}.{k[1]}', v) for k, v in sorted(m.items(), key=lambda p: p[0]))

    with create_text(blk_version_summary_path) as ostream:
        json.dump(sm, ostream, indent=2)


def test_collect_blk_names(bbfrespath: Path, blk_names_summary_path: Path):
    tag_modules = set()
    heap = []
    for path in bbf_paths(bbfrespath):
        with open(path, 'rb') as istream:
            istream.seek(12)
            tag = int.from_bytes(istream.read(2), 'little')
            if tag not in tag_modules:
                tag_modules.add(tag)
            rpath = str(path.relative_to(bbfrespath))
            p = path.stat().st_size, rpath
            heapq.heappush(heap, p)

    m = {
        'tag_modules': list(hex(tag) for tag in sorted(tag_modules)),
        'tiny files': [heapq.heappop(heap)[1] for _ in range(5)]
    }

    with create_text(blk_names_summary_path) as ostream:
        json.dump(m, ostream, indent=2)
