"""Проверка конструктора строк.
Блок строк из 'aces.vromfs.bin_u/gamedata/flightmodels/weaponpresets/f4u-1a_default.blk'
"""

from blk.binary.bbf_constructor import Strings


def test_parse(strings_istream, strings, strings_bs):
    parsed_strings = Strings.parse_stream(strings_istream)
    assert strings_istream.tell() == len(strings_bs)
    assert parsed_strings == strings


def test_build(iostream, strings, strings_bs):
    Strings.build_stream(strings, iostream)
    iostream.seek(0)
    build_bs = iostream.read()
    assert build_bs == strings_bs
