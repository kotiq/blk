import os
import json
import heapq
from collections import defaultdict, OrderedDict
import pytest
from helpers import make_outpath, create_text

outpath = make_outpath(__name__)


def bbf_files(path: str):
    for entry in os.scandir(path):  # type: os.DirEntry
        if entry.is_dir():
            yield from bbf_files(entry.path)  # @r
        elif entry.is_file() and entry.name.endswith('.blk'):
            with open(entry, 'rb') as istream:
                magic = istream.read(4)
                if magic == b'\x00BBF':
                    yield entry.path


@pytest.fixture(scope='module')
def blk_version_summary_path(outpath: str):
    return os.path.join(outpath, 'blk_version_summary.json')


@pytest.fixture(scope='module')
def blk_names_summary_path(outpath: str):
    return os.path.join(outpath, 'blk_names_summary.json')


def test_collect_blk_versions(bbfpath: str, blk_version_summary_path: str):
    m = defaultdict(list)
    for path in bbf_files(bbfpath):
        with open(path, 'rb') as istream:
            istream.seek(4)
            hi = int.from_bytes(istream.read(2), 'little')
            lo = int.from_bytes(istream.read(2), 'little')
            rpath = os.path.relpath(path, bbfpath)
            m[hi, lo].append(rpath)
    sm = OrderedDict((f'{k[0]}.{k[1]}', v) for k, v in sorted(m.items(), key=lambda p: p[0]))

    with create_text(blk_version_summary_path) as ostream:
        json.dump(sm, ostream, indent=2)


def test_collect_blk_names(bbfpath: str, blk_names_summary_path: str):
    tag_modules = set()
    heap = []
    for path in bbf_files(bbfpath):
        with open(path, 'rb') as istream:
            istream.seek(12)
            tag = int.from_bytes(istream.read(2), 'little')
            if tag not in tag_modules:
                tag_modules.add(tag)
            stat_ = os.stat(path)
            rpath = os.path.relpath(path, bbfpath)
            p = stat_.st_size, rpath
            heapq.heappush(heap, p)

    m = {
        'tag_modules': list(hex(tag) for tag in sorted(tag_modules)),
        'tiny files': [heapq.heappop(heap)[1] for _ in range(5)]
    }

    with create_text(blk_names_summary_path) as ostream:
        json.dump(m, ostream, indent=2)
