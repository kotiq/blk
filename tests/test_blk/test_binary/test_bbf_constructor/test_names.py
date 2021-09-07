"""Проверка конструктора имен.
Блок имен из 'aces.vromfs.bin_u/gamedata/flightmodels/weaponpresets/f4u-1a_default.blk'
"""

import io
import pytest
from blk.types import Name
from blk.binary.bbf_constructor import Names, NamesInit


@pytest.fixture(scope='module')
def names_bs():
    return bytes.fromhex(
        '0041 '
        '02 '
        '09 686964654E6F646573'
        '04 6E6F6465'
    )


@pytest.fixture(scope='module')
def names():
    return list(map(Name.of, (b'hideNodes', b'node')))


@pytest.fixture
def istream(names_bs):
    return io.BytesIO(names_bs)


@pytest.fixture
def iostream():
    return io.BytesIO()


@pytest.fixture()
def names_init(names):
    return NamesInit(0x100, names)


def test_parse(istream: io.BufferedIOBase, names_init: NamesInit, names_bs: bytes):
    parsed_names_init: NamesInit = Names.parse_stream(istream)
    assert istream.tell() == len(names_bs)
    assert list(parsed_names_init.names) == list(names_init.names)
    assert parsed_names_init.module == names_init.module


def test_build(iostream: io.BufferedIOBase, names_init: NamesInit, names_bs: bytes):
    Names.build_stream(names_init, iostream)
    iostream.seek(0)
    built_bs = iostream.read()
    assert built_bs == names_bs
