import os
import sys
import logging
import multiprocessing as mp
import typing as t
from functools import partial
import click
from multiprocessing_logging import install_mp_handler
import blk_unpack as bbf3
import blk.binary as bin
import blk.text as txt
import blk.json as jsn


logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.DEBUG, stream=sys.stdout)
install_mp_handler()
INDENT = ' '*4


def serialize_text(root, ostream, out_type, is_sorted):
    if out_type == bbf3.BLK.output_type['strict_blk']:
        return txt.serialize(root, ostream, dialect=txt.StrictDialect)
    elif out_type in map(bbf3.BLK.output_type.__getitem__, ('json', 'json_2')):
        return jsn.serialize(root, ostream, out_type, is_sorted)


def is_text(bs: bytes) -> bool:
    restricted = bytes.fromhex('00 01 02 03 04 05 06 07 08 0b 0c 0e 0f 10 11 12 14 13 15 16 17 18 19')
    return not any(b in restricted for b in bs)


def create_text(path):
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
    logging.info(file_path)

    try:
        with open(file_path, 'rb') as istream:
            bs = istream.read(4)
            # пустой файл
            if not bs:
                logging.info(f'{INDENT}Empty file')
                with open(out_path, 'wb') as _:
                    pass
            # файл прежнего формата
            elif bs in (b'\x00BBF', b'\x00BBz'):
                istream.seek(0)
                bs = istream.read()
                bbf3_parser = bbf3.BLK(bs)
                bs = bbf3_parser.unpack(out_type, is_sorted=False)
                with create_text(out_path) as ostream:
                    ostream.write(bs)
            # файл с именами в nm
            elif not bs[0]:
                if names is None:
                    nm_path = names_path(file_path, 'nm')
                    if nm_path:
                        logging.info(f'Loading NameMap from {nm_path!r}')
                        with open(nm_path, 'rb') as nm_istream:
                            names = bin.compose_names(nm_istream)
                if names:
                    istream.seek(0)
                    root = bin.compose_slim(names, istream)
                    with create_text(out_path) as ostream:
                        serialize_text(root, ostream, out_type, is_sorted)
                else:  # не найдена таблица имен
                    logging.error(f"{INDENT}NameMap not found")
            # файл с именами внутри или текст
            else:
                istream.seek(0)
                try:
                    root = bin.compose_fat(istream)
                    with create_text(out_path) as ostream:
                        serialize_text(root, ostream, out_type, is_sorted)
                except bin.ComposeError:  # текст
                    # рабочей грамматики у меня пока нет
                    # есть парсер текста на parsy, но без строк в тройных кавычках и вложенных комментариев
                    # поэтому, считаю, что текст корректный
                    # выполняется только простая проверка на мелкие значения
                    istream.seek(0)
                    bs = istream.read()
                    if is_text(bs):
                        logging.info(f'{INDENT}Copied as is')
                        with open(out_path, 'wb') as ostream:
                            ostream.write(bs)
                    else:
                        logging.info(f'{INDENT}Unknown file format')

    except (TypeError, EnvironmentError, bin.ComposeError) as e:
        logging.exception(f'{INDENT}{e}', exc_info=True)


def process_dir(dir_path: str, out_type: int, is_sorted: bool):
    entries = tuple(os.scandir(dir_path))

    for entry in entries:
        if entry.is_file() and os.path.basename(entry.path) == 'nm':
            nm_path = entry.path
            try:
                logging.info(f'Loading NameMap from {nm_path!r}')
                with open(nm_path, 'rb') as nm_istream:
                    names = bin.compose_names(nm_istream)

                process_slim_dir(dir_path, names, out_type, is_sorted)
                return
            except bin.ComposeError as e:
                logging.error(f'{nm_path}')
                logging.exception(f'{INDENT}{e}', exc_info=True)
                return

    dir_paths = []
    file_paths = []

    for entry in entries:
        if entry.is_dir():
            dir_paths.append(entry.path)
        elif entry.is_file():
            file_paths.append(entry.path)

    for dir_path in dir_paths:
        process_dir(dir_path, out_type, is_sorted)

    with mp.Pool(None) as pool:
        pool.map(partial(process_file, names=None, out_type=out_type, is_sorted=is_sorted), file_paths)
        pool.close()
        pool.join()


def file_paths_r(dir_path: str) -> t.Generator[str, None, None]:
    for entry in os.scandir(dir_path):
        if entry.is_dir():
            yield from file_paths_r(entry.path)
        elif entry.is_file():
            yield entry.path


def slim_dir_worker(queue: mp.JoinableQueue, names: t.Sequence, out_type: int, is_sorted: bool):
    for path in iter(queue.get, None):
        process_file(path, names, out_type, is_sorted)
        queue.task_done()
    queue.task_done()


def process_slim_dir(dir_path: str, names: t.Sequence, out_type: int, is_sorted: bool):
    file_paths = file_paths_r(dir_path)
    queue = mp.JoinableQueue()
    for path in file_paths:
        queue.put(path)
    ps = []
    for _ in range(mp.cpu_count()):
        p = mp.Process(target=slim_dir_worker, args=(queue, names, out_type, is_sorted))
        ps.append(p)
        p.daemon = True
        p.start()

    queue.join()

    for _ in ps:
        queue.put(None)

    queue.join()

    for p in ps:
        p.join()


@click.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--format', 'out_format', type=click.Choice(['strict_blk', 'json', 'json_2'], case_sensitive=False),
              default='json', show_default=True)
@click.option('--sort', 'is_sorted', is_flag=True, default=False)
def main(path: str, out_format: str, is_sorted: bool):
    out_type = bbf3.BLK.output_type[out_format]

    if os.path.isfile(path):
        process_file(path, None, out_type, is_sorted)
    else:
        process_dir(path, out_type, is_sorted)


if __name__ == '__main__':
    main()
