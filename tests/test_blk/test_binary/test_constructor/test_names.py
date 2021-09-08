"""Проверка конструктора имен.
Блок имен из 'game.vromfs.bin_u/gamedata/scenes/tank_compatibility_test_level.blk'"""

import io
import typing as t
import pytest
from blk.types import Name
from blk.binary.constructor import Names


@pytest.fixture(scope='module')
def names_bs_short():
    return bytes.fromhex(
        '2BA10'
        '6656E7469747900' '5F74656D706C61746500'
        '6C6576656C2E62696E00' '6C6576656C2E7765617468657200'
        '6C6576656C2E656E7669726F6E6D656E7400' '7761795F706F696E742E7472616E73666F726D00'
        '7761795F706F696E742E6E616D6500' '7761795F706F696E742E6D6F76655479706500'
        '7761795F706F696E742E737065656400' '726F7574652E726F757465496400'
        '726F7574652E776179506F696E74734E616D65733A6C6973743C743E00' '6E00'
        '73657474696E672E756E69745479706500' '73657474696E672E706C617965724E6F00' 
        '73657474696E672E636C6173734E616D6500' '73657474696E672E756E69745F636C61737300'
        '73657474696E672E6E616D6500' '73657474696E672E6F626A4C6179657200'
        '73657474696E672E636C6F7365645F776179706F696E747300' '73657474696E672E69735368697053706C696E6500'
        '73657474696E672E736869705475726E52616469757300' '73657474696E672E776561706F6E7300'
        '73657474696E672E61726D7900' '73657474696E672E636F756E7400'
        '73657474696E672E666F726D6174696F6E5F7479706500' '73657474696E672E666F726D6174696F6E5F64697600'
        '73657474696E672E666F726D6174696F6E5F7374657000' '73657474696E672E666F726D6174696F6E5F6E6F69736500'
        '73657474696E672E756E697175654E616D6500' '73657474696E672E61747461636B5F7479706500'
        '73657474696E672E746D00' '73657474696E672E62756C6C6574733A6C6973743C743E00'
        '73657474696E672E62756C6C657473436F756E743A6C6973743C693E00' '73657474696E672E726F7574654E616D6500'
        '73657474696E672E736B696E00' '73657474696E672E737065656400'
        '6261636B67726F756E645F6D6F64656C2E746D00' '6261636B67726F756E645F6D6F64656C2E6D6F64656C00'
        '6261636B67726F756E645F6D6F64656C2E756E69744E616D6500' '6261636B67726F756E645F6D6F64656C2E736B696E00'
        '6261636B67726F756E645F6D6F64656C2E776561706F6E00' '6261636B67726F756E645F6D6F64656C2E6E656564416E696D00'
        '6261636B67726F756E645F6D6F64656C2E62756C6C6574733A6C6973743C743E00'
    )


@pytest.fixture(scope='module')
def names():
    return list(map(Name.of, (
        b'entity', b'_template',
        b'level.bin', b'level.weather',
        b'level.environment', b'way_point.transform',
        b'way_point.name', b'way_point.moveType',
        b'way_point.speed', b'route.routeId',
        b'route.wayPointsNames:list<t>', b'n',
        b'setting.unitType', b'setting.playerNo',
        b'setting.className', b'setting.unit_class',
        b'setting.name', b'setting.objLayer',
        b'setting.closed_waypoints', b'setting.isShipSpline',
        b'setting.shipTurnRadius', b'setting.weapons',
        b'setting.army', b'setting.count',
        b'setting.formation_type', b'setting.formation_div',
        b'setting.formation_step', b'setting.formation_noise',
        b'setting.uniqueName', b'setting.attack_type',
        b'setting.tm', b'setting.bullets:list<t>',
        b'setting.bulletsCount:list<i>', b'setting.routeName',
        b'setting.skin', b'setting.speed',
        b'background_model.tm', b'background_model.model',
        b'background_model.unitName', b'background_model.skin',
        b'background_model.weapon', b'background_model.needAnim',
        b'background_model.bullets:list<t>')))


@pytest.fixture
def istream(names_bs_short):
    return io.BytesIO(names_bs)


@pytest.fixture
def iostream():
    return io.BytesIO()


def test_parse(istream: io.BufferedIOBase, names: t.Sequence[Name], names_bs: bytes):
    parsed_names = Names.parse_stream(istream)
    assert istream.tell() == len(names_bs)
    assert list(parsed_names) == list(names)


def test_build(iostream: io.BufferedIOBase, names: t.Sequence[Name], names_bs: bytes):
    Names.build_stream(names, iostream)
    iostream.seek(0)
    built_bs = iostream.read()
    assert built_bs == names_bs
