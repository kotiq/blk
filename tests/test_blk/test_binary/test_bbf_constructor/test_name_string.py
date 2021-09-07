import pytest
from blk.types import Name, Str
from blk.binary.bbf_constructor import types_cons_map


@pytest.mark.parametrize('cls', [Name, Str])
@pytest.mark.parametrize(['init', 'parse_bs', 'build_bs'], [
    pytest.param('hello', b'\x05hello', b'\x05hello', id='ascii'),
    pytest.param('привет',
                 b'\x0c\xd0\xbf\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x82',
                 b'\x0c\xd0\xbf\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x82', id='utf8'),
    pytest.param('привет',
                 b'\x06\xef\xf0\xe8\xe2\xe5\xf2',
                 b'\x0c\xd0\xbf\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x82', id='cp1251')
])
def test_name(cls, init, parse_bs, build_bs):
    name = Name.of(init)
    con = types_cons_map[cls]
    assert con.parse(parse_bs) == name
    assert con.build(name) == build_bs
