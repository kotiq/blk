import sys
from io import BytesIO
import pytest
from blk.types import *
from blk.binary.constructor import *
from blk.text.serializer import serialize


def make_sections_only_section():
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


sections_only_section = make_sections_only_section()
sections_only_section_fat_bs = bytes.fromhex(
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


@pytest.mark.parametrize(['section', 'bs'], [
    pytest.param(sections_only_section, sections_only_section_fat_bs, id='sections only section')
])
def test_fat(section, bs):
    stream = BytesIO()
    serialize_fat(section, stream)
    assert stream.getvalue() == bs

    stream.seek(0)
    s = compose_fat(stream)
    assert s == section

