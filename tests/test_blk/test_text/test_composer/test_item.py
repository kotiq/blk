import pytest
from pytest import param as _
from blk.types import (BlockComment, Color, Float, Float12, Float2, Float3, Float4, Int, Int2, Int3, LineComment, Long,
                       Name, Str, true)
from blk.text.composer import item


@pytest.mark.parametrize(['text', 'name', 'value'], [
    _('"bool":b = yes', Name('bool'), true, id='bool'),
    _('"int":i = 42', Name('int'), Int(42), id='int'),
    _('"long":i64 = 42', Name('long'), Long(42), id='long'),
    _('"float":r = 4.2', Name('float'), Float(4.2), id='float'),
    _('"str":t = "hello"', Name('str'), Str('hello'), id='str'),
    _('"int2":ip2 = 1, 2', Name('int2'), Int2((1, 2)), id='int2'),
    _('"int3":ip3 = 1, 2, 3', Name('int3'), Int3((1, 2, 3)), id='int3'),
    _('"color3":c = 1, 2, 3', Name('color3'), Color((1, 2, 3, 0xff)), id='color3'),
    _('"color4":c = 1, 2, 3, 4', Name('color4'), Color((1, 2, 3, 4)), id='color4'),
    _('"float2":p2 = 1.2, 3.4', Name('float2'), Float2((1.2, 3.4)), id='float2'),
    _('"float3":p3 = 1.2, 3.4, 5.6', Name('float3'), Float3((1.2, 3.4, 5.6)), id='float3'),
    _('"float4":p4 = 1.2, 3.4, 5.6, 7.8', Name('float4'), Float4((1.2, 3.4, 5.6, 7.8)), id='float4'),
    _('"float12":m = [[1.2, 3.4, 5.6] [7.8, 9.10, 11.12] [13.14, 15.16, 17.18] [19.20, 21.22, 23.24]]',
      Name('float12'),
      Float12((1.2, 3.4, 5.6, 7.8, 9.10, 11.12, 13.14, 15.16, 17.18, 19.20, 21.22, 23.24)), id='float12'),
])
def test_named_parameter(text, name, value):
    n, v = item.parse(text)
    assert isinstance(n, Name)
    assert isinstance(v, value.__class__)
    assert (n, v) == (name, value)


@pytest.mark.parametrize(['text', 'item_'], [
    _('//line comment', LineComment('line comment'), id='line'),
    _('/*block\ncomment*/', BlockComment('block\ncomment'), id='block'),
])
def test_comment(text, item_):
    parsed = item.parse(text)
    assert parsed == item_
