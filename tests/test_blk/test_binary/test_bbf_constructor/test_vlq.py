import pytest
from pytest import param as _
from blk.binary.bbf_constructor import VLQ


@pytest.mark.parametrize(['x', 'parse_bs', 'build_bs'], [
    _(0x00, b'\x00', b'\x00', id='1 byte min'),
    _(0x7f, b'\x7f', b'\x7f', id='1 byte max'),
    _(0x80, b'\x80\x80', b'\x80\x80', id='2 bytes min'),
    _(0x3f_ff, b'\xbf\xff', b'\xbf\xff', id='2 bytes max'),
    _(0x40_00, b'\xc0\x40\x00', b'\xc0\x40\x00', id='3 bytes min'),
    _(0x3f_ff_ff, b'\xff\xff\xff', b'\xff\xff\xff', id='3 bytes max'),
])
def test_vlq(x, parse_bs, build_bs):
    assert VLQ.parse(parse_bs) == x
    assert VLQ.build(x) == build_bs
