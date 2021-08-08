import os
import sys
from traceback import print_exc
import typing as t
import click
import blk_unpack as bbf3
import blk.binary as bin
import blk.text as txt
import blk.json as jsn


INDENT = ' '*4


def serialize_text(root, ostream, out_type, is_sorted):
    if out_type == bbf3.BLK.output_type['strict_blk']:
        return txt.serialize(root, ostream, dialect=txt.StrictDialect)
    elif out_type in map(bbf3.BLK.output_type.__getitem__, ('json', 'json_2')):
        return jsn.serialize(root, ostream, out_type, is_sorted)


def is_text(bs: bytes) -> bool:
    restricted = bytes.fromhex('00 01 02 03 04 05 06 07 08 0b 0c 0e 0f 10 11 12 14 13 15 16 17 18 19')
    return not any(b in restricted for b in bs)


def creat_text(path):
    return open(path, 'w', newline='', encoding='utf8')


def names_path(file_path: str, nm: str):
    file_path = os.path.abspath(file_path)
    drive, _ = os.path.splitdrive(file_path)
    root = drive + os.path.sep

    dir_path = os.path.dirname(file_path)
    nm_path = os.path.join(dir_path, nm)
    if nm_path and os.path.isfile(nm_path):
        return nm_path

    while dir_path != root:
        dir_path = os.path.dirname(dir_path)
        nm_path = os.path.join(dir_path, nm)
        if nm_path and os.path.isfile(nm_path):
            return nm_path

    return None


def process_file(file_path: str, names: t.Optional[t.Sequence], out_type: int, is_sorted: bool):
    if not file_path.endswith('.blk'):
        return

    out_path = file_path + 'x'
    print(file_path)

    try:
        with open(file_path, 'rb') as istream:
            bs = istream.read(4)
            # пустой файл
            if not bs:
                print(f'{INDENT}Empty file')
                with open(out_path, 'wb') as _:
                    pass
            # файл прежнего формата
            elif bs in (b'\x00BBF', b'\x00BBz'):
                istream.seek(0)
                bs = istream.read()
                bbf3_parser = bbf3.BLK(bs)
                bs = bbf3_parser.unpack(out_type, is_sorted=False)
                with creat_text(out_path) as ostream:
                    ostream.write(bs)
            # файл с именами в nm
            elif not bs[0]:
                if names is None:
                    nm_path = names_path(file_path, 'nm')
                    if nm_path:
                        with open(nm_path, 'rb') as nm_istream:
                            names = bin.compose_names(nm_istream)
                if names:
                    istream.seek(0)
                    root = bin.compose_slim(names, istream)
                    with creat_text(out_path) as ostream:
                        serialize_text(root, ostream, out_type, is_sorted)
                else:  # не найдена таблица имен
                    print(f"{INDENT}NameMap not found")
            # файл с именами внутри или текст
            else:
                istream.seek(0)
                try:
                    root = bin.compose_fat(istream)
                    with creat_text(out_path) as ostream:
                        serialize_text(root, ostream, out_type, is_sorted)
                except bin.ComposeError:  # текст
                    # рабочей грамматики у меня пока нет
                    # есть парсер текста на parsy, но без строк в тройных кавычках и вложенных комментариев
                    # поэтому, считаю, что текст корректный
                    # выполняется только простая проверка на мелкие значения
                    istream.seek(0)
                    bs = istream.read()
                    if is_text(bs):
                        print(f'{INDENT}Copied as is')
                        with open(out_path, 'wb') as ostream:
                            ostream.write(bs)
                    else:
                        print(f'{INDENT}Unknown file format')

    except (TypeError, EnvironmentError, bin.ComposeError) as e:
        print(f'{INDENT}{e}')
        print_exc(file=sys.stdout)


def process_dir(dir_path: str, out_type: int, is_sorted: bool):
    entries = tuple(os.scandir(dir_path))

    for entry in entries:
        if entry.is_file() and os.path.basename(entry.path) == 'nm':
            nm_path = entry.path
            try:
                with open(nm_path, 'rb') as nm_istream:
                    names = bin.compose_names(nm_istream)

                process_slim_dir(dir_path, names, out_type, is_sorted)
                return
            except bin.ComposeError as e:
                print(f'{nm_path}')
                print(f'{INDENT}{e}')
                return

    for entry in entries:
        if entry.is_dir():
            process_dir(entry.path, out_type, is_sorted)
        elif entry.is_file():
            process_file(entry.path, None, out_type, is_sorted)


def process_slim_dir(dir_path: str, names: t.Sequence, out_type: int, is_sorted: bool, ):
    for entry in os.scandir(dir_path):
        if entry.is_dir():
            process_slim_dir(entry.path, names, out_type, is_sorted)
        elif entry.is_file():
            process_file(entry.path, names, out_type, is_sorted)


@click.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--format', 'out_format', type=click.Choice(['strict_blk', 'json', 'json_2'], case_sensitive=False), default='json',
              show_default=True)
@click.option('--sort', 'is_sorted', is_flag=True, default=False)
def main(path: str, out_format: str, is_sorted: bool):
    out_type = bbf3.BLK.output_type[out_format]

    if os.path.isfile(path):
        process_file(path, None, out_type, is_sorted)
    else:
        process_dir(path, out_type, is_sorted)


if __name__ == '__main__':
    main()
