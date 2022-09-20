from argparse import Action, ArgumentParser, ArgumentTypeError, Namespace
import logging
from pathlib import Path
from sys import exit
from typing import NamedTuple, Optional
from blk import Format
from blk.directory import Directory


class Args(NamedTuple):
    @classmethod
    def from_namespace(cls, ns: Namespace) -> 'Args':
        return cls(**vars(ns))

    nm_path: Optional[Path]
    dict_path: Optional[Path]
    out_format: Format
    is_sorted: bool
    is_minified: bool
    exit_first: bool
    out_path: Optional[Path]
    is_flat: bool
    loglevel: str
    in_path: Path


def iname(f: Format) -> str:
    return f.name.lower()


def format_(s: str) -> Format:
    return Format[s.upper()]


def get_logger(name: str) -> logging.Logger:
    formatter = logging.Formatter('%(created)f %(levelname)s %(message)s')
    logger_ = logging.getLogger(name)
    logger_.level = logging.DEBUG
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger_.addHandler(console_handler)

    return logger_


logger = get_logger('blk')


class CreateFormat(Action):
    def __call__(self, parser: ArgumentParser, namespace: Namespace, values: str, option_string=None) -> None:
        f = format_(values)
        setattr(namespace, self.dest, f)


class CreateLogLevel(Action):
    def __call__(self, parser: ArgumentParser, namespace: Namespace, values: str, option_string=None) -> None:
        level = values.upper()
        setattr(namespace, self.dest, level)


def file_path(value: str) -> Path:
    path = Path(value)
    if not path.is_file():
        raise ArgumentTypeError('Не является файлом: {!r}'.format(str(path)))
    return path


def file_dir_path(value) -> Path:
    path = Path(value)
    if not path.exists():
        raise ArgumentTypeError('Нет доступа к объекту: {!r}'.format(str(path)))
    elif not (path.is_file() or path.is_dir()):
        mode = path.stat().st_mode
        raise ArgumentTypeError('Не файл или директория: {:#o}: {!r}'.format(mode, str(path)))
    return path


def get_args() -> Args:
    parser = ArgumentParser(description='Распаковщик blk файлов.')
    parser.add_argument('--nm', dest='nm_path', type=file_path, default=None,
                        help='Путь карты имен.')
    parser.add_argument('--dict', dest='dict_path', type=file_path, default=None,
                        help='Путь словаря.')
    parser.add_argument('--format', dest='out_format', choices=sorted(map(iname, Format)),
                        action=CreateFormat, default=Format.JSON,
                        help='Формат блоков. По умолчанию {}.'.format(iname(Format.JSON)))
    parser.add_argument('--sort', dest='is_sorted', action='store_true', default=False,
                        help='Сортировать ключи для JSON*.')
    parser.add_argument('--minify', dest='is_minified', action='store_true', default=False,
                        help='Минифицировать JSON*.')
    parser.add_argument('-x', '--exitfirst', dest='exit_first', action='store_true', default=False,
                        help='Закончить распаковку при первой ошибке.')
    parser.add_argument('-o', '--output', dest='out_path', type=Path, default=None,
                        help=('Выходная директория для распаковки. Если output не указан, выходная директория для '
                              "распаковки совпадает со входной, к расширению файлов добавляется 'x'."))
    parser.add_argument('--flat', dest='is_flat', action='store_true', default=False,
                        help='Плоская выходная структура.')
    parser.add_argument('--loglevel', action=CreateLogLevel, choices=('critical', 'error', 'warning', 'info', 'debug'),
                        default='INFO',
                        help='Уровень сообщений. По умолчанию info.')
    parser.add_argument(dest='in_path', type=file_dir_path,
                        help='Путь, содержащий упакованные файлы.')

    args = parser.parse_args()
    return Args.from_namespace(args)


def main() -> int:
    args = get_args()
    logger.setLevel(args.loglevel)

    if args.in_path.is_file():
        source_root = args.in_path.absolute().parent
        rel_paths = [Path(args.in_path.name)]
    elif args.in_path.is_dir():
        source_root = args.in_path.absolute()
        rel_paths = None
    # иначе отсекается парсером командной строки

    target_root = source_root if args.out_path is None else args.out_path
    directory = Directory(source_root, target_root, args.nm_path, args.dict_path)

    failed = successful = 0
    try:
        logger.info('Начало распаковки.')
        for result in directory.unpack_iter(rel_paths, target_root, args.is_flat,
                                            args.out_format, args.is_sorted, args.is_minified):
            source = source_root / result.path
            if result.error is not None:
                failed += 1
                logger.info('[FAIL] {!r}: {}'.format(str(source), result.error))
                if args.exit_first:
                    break
            else:
                logger.info('[ OK ] {!r}'.format(str(source)))
                successful += 1

        logger.info('Успешно распаковано: {}/{}'.format(successful, successful+failed))
        if failed:
            logger.info('Ошибка при распаковке файлов.')
            return 1

    except Exception as e:
        logger.error('Ошибка при распаковке файлов.')
        logger.exception(e)
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
