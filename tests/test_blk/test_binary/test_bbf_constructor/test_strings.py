"""Проверка конструктора строк.
Блок строк из 'aces.vromfs.bin_u/gamedata/flightmodels/weaponpresets/f4u-1a_default.blk'
"""

import io
import typing as t
import pytest
from blk.types import Str
from blk.binary.bbf_constructor import Strings


@pytest.fixture(scope='module')
def strings_bs():
    return bytes.fromhex(
        '06000040 '
        '01'
        '05 70796C6F6E'
    )


@pytest.fixture(scope='module')
def strings():
    return list(map(Str.of, (b'pylon', )))


@pytest.fixture
def istream(strings_bs):
    return io.BytesIO(strings_bs)


@pytest.fixture
def iostream():
    return io.BytesIO()


def test_parse(istream: io.BufferedIOBase, strings: t.Sequence[Str], strings_bs: bytes):
    parsed_strings: t.Sequence[Str] = Strings.parse_stream(istream)
    assert istream.tell() == len(strings_bs)
    assert list(parsed_strings) == list(strings)


def test_build(iostream: io.BufferedIOBase, strings: t.Sequence[Str], strings_bs: bytes):
    Strings.build_stream(strings, iostream)
    iostream.seek(0)
    build_bs = iostream.read()
    assert build_bs == strings_bs
