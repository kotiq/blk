"""Проверка конструктора блока.
Блок из 'aces.vromfs.bin_u/gamedata/flightmodels/weaponpresets/f4u-1a_default.blk'
"""

import io
import typing as t
from blk.binary.bbf_constructor import Block, ValueInfo


def test_parse(block_istream: io.BufferedIOBase, values_info: t.List[ValueInfo], block_bs: bytes):
    parsed_values_info: t.List[ValueInfo] = Block.parse_stream(block_istream)
    assert block_istream.tell() == len(block_bs)
    assert parsed_values_info == values_info

