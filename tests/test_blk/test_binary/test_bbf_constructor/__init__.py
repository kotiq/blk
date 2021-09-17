import os


def bbf_paths(dir_path):
    for entry in os.scandir(dir_path):  # type: os.DirEntry
        if entry.is_dir():
            yield from bbf_paths(entry.path)  # @r
        elif entry.is_file():
            if entry.name.endswith('.blk') and entry.stat().st_size > 12:
                with open(entry, 'rb') as istream:
                    bs = istream.read(4)
                if bs == b'\x00BBF':
                    yield entry.path
