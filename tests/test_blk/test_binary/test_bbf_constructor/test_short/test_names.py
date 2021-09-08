"""Проверка конструктора параметров отображения имен.
Блок имен из 'aces.vromfs.bin_u/gamedata/flightmodels/weaponpresets/f4u-1a_default.blk'
"""

import io
import typing as t
from blk.types import Name
from blk.binary.bbf_constructor import NamesMapInit, NamesMapInitContainer, NamesMapAdapter


def test_parse(names_istream: io.BufferedIOBase, names_map_init: NamesMapInitContainer, names_bs: bytes):
    parsed_names_init: NamesMapInitContainer = NamesMapInit.parse_stream(names_istream)
    assert names_istream.tell() == len(names_bs)
    assert list(parsed_names_init.raw_names) == list(names_map_init.raw_names)
    assert parsed_names_init.module == names_map_init.module


def test_build(iostream: io.BufferedIOBase, names_map_init: NamesMapInitContainer, names_bs: bytes):
    NamesMapInit.build_stream(names_map_init, iostream)
    iostream.seek(0)
    built_bs = iostream.read()
    assert built_bs == names_bs


def test_decode(names_map_init: NamesMapInitContainer, names_map: t.Mapping[int, Name]):
    decoded_names_map = NamesMapAdapter._decode(None, names_map_init, None, None)
    assert decoded_names_map == names_map
