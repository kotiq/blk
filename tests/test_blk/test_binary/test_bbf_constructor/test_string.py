import pytest
from pytest import param as _
from blk.types import Str
from blk.binary.bbf_constructor import String


@pytest.mark.parametrize(['init', 'parse_bs', 'build_bs'], [
    _('hello', b'\x05hello', b'\x05hello', id='ascii'),
    _('привет', b'\x0c\xd0\xbf\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x82',
                b'\x0c\xd0\xbf\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x82', id='utf8'),
    _('привет', b'\x06\xef\xf0\xe8\xe2\xe5\xf2',
                b'\x0c\xd0\xbf\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x82', id='cp1251')
])
def test_str(init, parse_bs, build_bs):
    string = Str.of(init)
    assert String.parse(parse_bs) == string
    assert String.build(string) == build_bs
