# to remove comments https://github.com/jleffler/scc-snapshots

from argparse import ArgumentParser, Namespace
from io import BytesIO, StringIO
from pathlib import Path
from re import compile
from subprocess import CalledProcessError, PIPE, run
from typing import BinaryIO, Iterable, TextIO
import sys


def get_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('-o', '--output', type=Path, help='Выходная директория.')
    parser.add_argument('input', type=Path, help='Входная директория.')
    return parser.parse_args()


def lines_decode(bytes_it: Iterable[bytes]) -> Iterable[str]:
    encodings = ('utf8', 'cp1251')

    for bs in bytes_it:
        for e in encodings:
            try:
                yield bs.decode(e)
            except UnicodeDecodeError:
                continue

        raise ValueError('Не удалось декодировать как {} последовательность: {}'
                         .format('|'.join(encodings), bs))


def decode(istream: BytesIO, ostream: TextIO):
    for line in lines_decode(istream):
        ostream.write(line)


def remove_comments(text: str, ostream: TextIO) -> str:
    proc = run(['scc', str(Path)], input=text, stdout=PIPE, stderr=PIPE, encoding='utf8')
    if not proc.returncode and not proc.stderr:
        ostream.write(proc.stdout)

    return proc.stderr if proc.stderr else ''


def unfold(text: str) -> str:
    return text.replace(';', '\n')


def text_blk_paths(path: Path) -> Iterable[Path]:
    for p in path.rglob('*.blk'):
        try:
            if not p.stat().st_size:
                print('[SKIP] Пустой файл: {}'.format(p))
                continue
            with p.open('rb') as istream:
                first = istream.read(1)[0]
                if first <= 5:
                    print('[SKIP] Двоичный файл: {}'.format(p))
                    continue
        except EnvironmentError:
            print('[SKIP] EnvironmentError: {}'.format(p))
            continue
        else:
            yield p


def main() -> int:
    args = get_args()
    print(args)
    if not args.input.exists():
        print('Нет входной директории: {}'.format(args.input), file=sys.stderr)
        return 1
    list(text_blk_paths(args.input))

    return 0


if __name__ == '__main__':
    sys.exit(main())


