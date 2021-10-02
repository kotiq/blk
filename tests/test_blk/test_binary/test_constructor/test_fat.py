import io
import pytest
from pytest_lazyfixture import lazy_fixture
from blk.types import *
from blk.binary.constructor import *


@pytest.fixture(scope='module')
def sections_only_section():
    a = Section()
    b = Section()
    c = Section()
    d = Section()
    e = Section()
    f = Section()
    g = Section()
    h = Section()
    i = Section()
    j = Section()
    k = Section()
    l = Section()

    a.append(Name('b'), b)
    a.append(Name('c'), c)
    a.append(Name('d'), d)
    a.append(Name('e'), e)

    c.append(Name('f'), f)
    c.append(Name('g'), g)

    e.append(Name('h'), h)
    e.append(Name('i'), i)
    e.append(Name('j'), j)

    g.append(Name('k'), k)
    g.append(Name('l'), l)

    return a


@pytest.fixture(scope='module')
def sections_only_section_fat_bs():
    return bytes.fromhex(
        '0b'  # names_count
        '16'  # names_bytes_count
        '6200 6300 6600 6700 6b00 6c00 6400 6500 6800 6900 6a00'  # names_bytes
        '0c'  # blocks_count
        '00'  # params_count
        '00'  # params_data
        '00 00 04 01'  # blocks_count
        '01 00 00'
        '02 00 02 05'
        '07 00 00'
        '08 00 03 07'
        '03 00 00'
        '04 00 02 0a'
        '09 00 00'
        '0a 00 00'
        '0b 00 00'
        '05 00 00'
        '06 00 00'
    )


@pytest.fixture
def iostream():
    return io.BytesIO()


sections_only_section_ = lazy_fixture('sections_only_section')
sections_only_section_fat_bs_ = lazy_fixture('sections_only_section_fat_bs')


@pytest.mark.parametrize(['section', 'bs'], [
    pytest.param(sections_only_section_, sections_only_section_fat_bs_, id='sections only section')
])
def test_fat(section, iostream, bs):
    serialize_fat_data(section, iostream)
    assert iostream.tell() == len(bs)
    iostream.seek(0)
    built_bs = iostream.read()
    assert built_bs == bs

    iostream.seek(0)
    s = compose_fat_data(iostream)
    assert s == section
