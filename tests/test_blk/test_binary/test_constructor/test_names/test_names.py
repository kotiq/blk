"""Проверка конструктора имен.
Блок имен из 'game.vromfs.bin_u/gamedata/scenes/tank_compatibility_test_level.blk'"""

from blk.binary.constructor import Names


def test_parse(names_istream, names, names_bs):
    parsed_names = Names.parse_stream(names_istream)
    assert names_istream.tell() == len(names_bs)
    assert list(parsed_names) == list(names)


def test_build(iostream, inv_names, names_bs):
    Names.build_stream(inv_names, iostream)
    iostream.seek(0)
    built_bs = iostream.read()
    assert built_bs == names_bs
