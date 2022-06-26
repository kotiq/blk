import pytest
from pytest import param as _
from blk.types import Bool, Color, Int, Int2, Int3, Float, Float2, Float3, Float4, Float12, Long, Str
from blk.binary.constructor import ParamInfoCon, types_codes_map
from . import _test_parse_all


@pytest.mark.parametrize(['bs_hex', 'info'], [
    _('012345 01 01234567', (0x452301, Str, '01234567'), id='Str'),
    _('6789ab 02 89abcdef', (0xab8967, Int, '89abcdef'), id='Int'),
    _('cdef01 03 01234567', (0x01efcd, Float, '01234567'), id='Float'),
    _('234567 04 89abcdef', (0x674523, Float2, '89abcdef'), id='Float2'),
    _('89abcd 05 01234567', (0xcdab89, Float3, '01234567'), id='Float3'),
    _('ef0123 06 89abcdef', (0x2301ef, Float4, '89abcdef'), id='Float4'),
    _('456789 07 01234567', (0x896745, Int2, '01234567'), id='Int2'),
    _('abcdef 08 89abcdef', (0xefcdab, Int3, '89abcdef'), id='Int3'),
    _('012345 09 00000000', (0x452301, Bool, '00000000'), id='false'),
    _('6789ab 09 01000000', (0xab8967, Bool, '01000000'), id='true'),
    _('cdef01 0a 01234567', (0x01efcd, Color, '01234567'), id='Color'),
    _('234567 0b 89abcdef', (0x674523, Float12, '89abcdef'), id='Float12'),
    _('89abcd 0c 01234567', (0xcdab89, Long, '01234567'), id='Long'),

])
def test_con(bs_hex, info):
    bs = bytes.fromhex(bs_hex)
    name_id, cls, data_hex = info
    code = types_codes_map[cls]
    info = name_id, code, bytes.fromhex(data_hex)
    _test_parse_all(ParamInfoCon, bs, info.__eq__)
    assert ParamInfoCon.build(info) == bs
