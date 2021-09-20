from pathlib import Path


def bbf_paths(path: Path):
    for p in path.iterdir():
        if p.is_dir():
            yield from bbf_paths(p)  # @r
        elif p.is_file():
            if p.name.endswith('.blk') and p.stat().st_size > 12:
                with open(p, 'rb') as istream:
                    bs = istream.read(4)
                if bs == b'\x00BBF':
                    yield p
