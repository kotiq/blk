import pytest
from blk.binary.bbf_constructor import RawPascalString


@pytest.mark.parametrize(['init', 'parse_bs', 'build_bs'], [
    pytest.param(b'hello', b'\x05hello', b'\x05hello', id='ascii'),
    pytest.param(b'\xd0\xbf\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x82',
                 b'\x0c\xd0\xbf\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x82',
                 b'\x0c\xd0\xbf\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x82', id='utf8'),
    pytest.param(b'\xef\xf0\xe8\xe2\xe5\xf2',
                 b'\x06\xef\xf0\xe8\xe2\xe5\xf2',
                 b'\x06\xef\xf0\xe8\xe2\xe5\xf2', id='cp1251')
])
def test_raw_pascal_string(init, parse_bs, build_bs):
    assert RawPascalString.parse(parse_bs) == init
    assert RawPascalString.build(init) == build_bs
