from itertools import chain
import logging
from os import PathLike
from pathlib import Path
from typing import Iterable, Iterator, NamedTuple, Optional, Sequence, TextIO
from zstandard import ZstdCompressionDict, ZstdDecompressor
import blk.text as txt
import blk.json as jsn
from blk import Format, Section
from blk.binary import (BlkType, ComposeError, NO_DICT_EXPECTED, compose_names, compose_partial_fat_zst,
                        compose_partial_bbf, compose_partial_bbf_zlib, compose_partial_fat, compose_partial_slim,
                        compose_partial_slim_zst)
from .error import NameUnpackError, DictUnpackError

__all__ = [
    'Directory',
]

logger = logging.getLogger(__name__)


def serialize_text(root: Section, ostream: TextIO, out_format: Format, is_sorted: bool, is_minified: bool) -> None:
    if out_format is Format.STRICT_BLK:
        txt.serialize(root, ostream, dialect=txt.StrictDialect)
    elif out_format in (Format.JSON, Format.JSON_2, Format.JSON_3):
        jsn.serialize(root, ostream, out_format, is_sorted, is_minified)


def is_text(bs: Iterable[bytes]) -> bool:
    restricted = bytes.fromhex('00 01 02 03 04 05 06 07 08 0b 0c 0e 0f 10 11 12 14 13 15 16 17 18 19')
    return not any(b in restricted for b in bs)


def create_text(path: PathLike) -> TextIO:
    return open(path, 'w', newline='', encoding='utf8')


class ExtractResult(NamedTuple):
    path: Path
    error: Optional[Exception]


class Directory:
    """
    Директория представляет директорию распаковки образа VROMFS.
    Если образ содержал карту имен и словарь, они расположены в корне директории.
    """

    def __init__(self, source_root: Path, target_root: Path,
                 nm_path: Optional[Path] = None, dict_path: Optional[Path] = None) -> None:
        self.source_root = source_root
        self.target_root = target_root
        self._names: Optional[Sequence[str]] = ...
        self._dict_is_set = False
        self._decompressor: Optional[ZstdDecompressor] = ...

        if dict_path is not None:
            self.set_dict_decompressor(dict_path)
        else:
            self._decompressor = None

        if nm_path is not None:
            self.set_names(nm_path)
        else:
            self._names = None

    def set_names(self, nm_path: Path) -> None:
        try:
            with open(nm_path, 'rb') as istream:
                ns = compose_names(istream, self.decompressor)
                self._names = ns.names
                logger.debug('Разделяемая карта имен {}'.format(ns.table_digest.hex()))
                if ns.dict_digest != NO_DICT_EXPECTED:
                    logger.debug('Ожидаемое имя словаря: {}.dict'.format(ns.dict_digest.hex()))
        except FileNotFoundError:
            pass
        except ComposeError as e:
            raise NameUnpackError from e

    def set_dict_decompressor(self, dict_path: Path) -> None:
        try:
            with open(dict_path, 'rb') as istream:
                data = istream.read()
                dict_ = ZstdCompressionDict(data)
                self._decompressor = ZstdDecompressor(dict_data=dict_)
                self._dict_is_set = True
                logger.debug('Загружен словарь: {!r}'.format(str(dict_path)))
        except OSError as e:
            raise DictUnpackError from e

    @property
    def names(self) -> Optional[Sequence[str]]:
        if self._names is None:
            self.set_names(self.source_root / 'nm')
        return self._names

    @property
    def decompressor(self) -> Optional[ZstdDecompressor]:
        if self._decompressor is None:
            dict_paths = list(self.source_root.glob('*.dict'))
            if not dict_paths:
                self._decompressor = ZstdDecompressor()
            else:
                self.set_dict_decompressor(self.source_root / dict_paths[0])

        return self._decompressor

    def _unpack_file_into_blk(self, rel_path: Path, ostream: TextIO,
                              out_format: Format, is_sorted: bool, is_minified: bool) -> None:
        source = self.source_root / rel_path
        with open(source, 'rb') as istream:
            fst = istream.read(1)
            if not fst:
                logger.debug('{!r}: EMPTY'.format(str(source)))
                return

            blk_type = BlkType.from_byte(fst)
            try:
                head = b''

                if blk_type in (BlkType.SLIM, BlkType.SLIM_ZST, BlkType.SLIM_ZST_DICT):
                    if self.names is None:
                        raise NameUnpackError('Не указана карта имен.')
                if blk_type is BlkType.SLIM_ZST_DICT:
                    if self.decompressor is not None and not self._dict_is_set:
                        raise DictUnpackError('Не указан словарь.')

                if blk_type is BlkType.FAT:
                    section = compose_partial_fat(istream)
                elif blk_type is BlkType.FAT_ZST:
                    section = compose_partial_fat_zst(istream, self.decompressor)
                elif blk_type is BlkType.SLIM:
                    section = compose_partial_slim(self.names, istream)
                elif blk_type in (BlkType.SLIM_ZST, BlkType.SLIM_ZST_DICT):
                    section = compose_partial_slim_zst(self.names, istream, self.decompressor)
                elif blk_type is BlkType.BBF:
                    triple = istream.read(3)
                    if triple == b'BBF':
                        section = compose_partial_bbf(istream)
                    elif triple == b'BBz':
                        section = compose_partial_bbf_zlib(istream)
                    else:
                        section = None
                        head = fst + triple
                else:
                    section = None
                    head = fst

                if section is None:
                    bs = istream.read()
                    ostream.flush()
                    if head:
                        ostream.buffer.write(head)
                    ostream.buffer.write(bs)
                    out_format_name = 'TEXT' if is_text(chain(head, bs)) else 'UNKNOWN'
                else:
                    serialize_text(section, ostream, out_format, is_sorted, is_minified)
                    out_format_name = out_format.name
                logger.debug('{!r}: {} => {}'.format(str(source), blk_type.name, out_format_name))
            except Exception:
                logger.debug('{!r}: {}'.format(str(source), blk_type.name))
                raise

    def _unpack_file(self, rel_path: Path, target_root: Path, is_flat: bool,
                     out_format: Format, is_sorted: bool, is_minified: bool) -> Path:
        target_rel_path = rel_path.name if is_flat else rel_path
        target = target_root / target_rel_path
        if target.exists():
            target = target.with_suffix(target.suffix + 'x')

        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_name(target.name + '~')

        with create_text(tmp) as ostream:
            self._unpack_file_into_blk(self.source_root / rel_path, ostream, out_format, is_sorted, is_minified)
            ostream.close()
            tmp.replace(target)

        return target

    def unpack_iter(self, rel_paths: Optional[Iterable[Path]] = None, target_root: Optional[Path] = None,
                    is_flat: bool = False, out_format: Format = Format.JSON, is_sorted: bool = False,
                    is_minified: bool = False) -> Iterator[ExtractResult]:
        if rel_paths is None:
            rel_paths = map(lambda p: p.relative_to(self.source_root), tuple(self.source_root.rglob('*.blk')))

        if target_root is None:
            target_root = Path.cwd()

        for rel_path in rel_paths:
            source = self.source_root / rel_path

            try:
                source.stat()
                self._unpack_file(rel_path, target_root, is_flat, out_format, is_sorted, is_minified)
            except Exception as e:
                yield ExtractResult(rel_path, e)
            else:
                yield ExtractResult(rel_path, None)

    def unpack_file(self, rel_path: Path, target_root: Optional[Path] = None, is_flat: bool = False,
                    out_format: Format = Format.JSON, is_sorted: bool = False, is_minified: bool = False
                    ) -> ExtractResult:
        return next(self.unpack_iter([rel_path], target_root, is_flat, out_format, is_sorted, is_minified))
