"""Проверка конструктора параметров отображения имен.
Блок имен из 'aces.vromfs.bin_u/gamedata/flightmodels/weaponpresets/f4u-1a_default.blk'
"""

from blk.binary.bbf_constructor import InvNamesMap, Names, NamesMap


def test_parse(names_istream, names_map: NamesMap, names_bs):
    parsed_names_map = Names.parse_stream(names_istream)
    assert names_istream.tell() == len(names_bs)
    assert parsed_names_map == names_map


def test_build(iostream, inv_names_map: InvNamesMap, names_bs):
    module = 0x100
    Names.build_stream(inv_names_map, iostream, module=module)
    iostream.seek(0)
    built_bs = iostream.read()
    assert built_bs == names_bs
