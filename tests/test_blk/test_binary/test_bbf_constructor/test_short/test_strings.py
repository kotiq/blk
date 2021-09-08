"""Проверка конструктора строк.
Блок строк из 'aces.vromfs.bin_u/gamedata/flightmodels/weaponpresets/f4u-1a_default.blk'
"""

import io
import typing as t
from blk.types import Str
from blk.binary.bbf_constructor import Strings


def test_parse(strings_istream: io.BufferedIOBase, strings: t.List[Str], strings_bs: bytes):
    parsed_strings: t.List[Str] = Strings.parse_stream(strings_istream)
    assert strings_istream.tell() == len(strings_bs)
    assert parsed_strings == strings


def test_build(iostream: io.BufferedIOBase, strings: t.List[Str], strings_bs: bytes):
    Strings.build_stream(strings, iostream)
    iostream.seek(0)
    build_bs = iostream.read()
    assert build_bs == strings_bs
