import pytest
from pytest import param as _
from blk.types import Name
from blk.binary.constructor import NameCon


@pytest.mark.parametrize(['init', 'parse_bs', 'build_bs'], [
    _('hello', b'hello\x00', b'hello\x00', id='ascii'),
    _('привет',
      b'\xd0\xbf\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x82\x00',
      b'\xd0\xbf\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x82\x00', id='utf8'),
    _('привет',
      b'\xef\xf0\xe8\xe2\xe5\xf2\x00',
      b'\xd0\xbf\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x82\x00', id='cp1251')
])
def test_name(init, parse_bs, build_bs):
    name = Name.of(init)
    assert NameCon.parse(parse_bs) == name
    assert NameCon.build(name) == build_bs


