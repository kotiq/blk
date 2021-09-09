import pytest
from blk.types import Name as Name_
from blk.binary.constructor import Name


@pytest.mark.parametrize(['init', 'parse_bs', 'build_bs'], [
    pytest.param('hello', b'hello\x00', b'hello\x00', id='ascii'),
    pytest.param('привет',
                 b'\xd0\xbf\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x82\x00',
                 b'\xd0\xbf\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x82\x00', id='utf8'),
    pytest.param('привет',
                 b'\xef\xf0\xe8\xe2\xe5\xf2\x00',
                 b'\xd0\xbf\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x82\x00', id='cp1251')
])
def test_name(init, parse_bs, build_bs):
    name = Name_.of(init)
    assert Name.parse(parse_bs) == name
    assert Name.build(name) == build_bs


