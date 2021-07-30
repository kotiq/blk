import os
from .blk_unpack_demo import is_text


def test_is_text(cdkpath):
    def process_file(path):
        if path.endswith('.blk'):
            with open(path, 'rb') as istream:
                bs = istream.read()
            assert is_text(bs)

    def process_dir(path):
        for entry in os.scandir(path):
            if entry.is_file():
                process_file(entry.path)
            elif entry.is_dir():
                process_dir(entry.path)

    process_dir(cdkpath)
