from io import StringIO
import pytest
from blk.types import Name, Int
from blk.text.serializer import serialize_pair
from . import simple_context


context_hex = simple_context({'int': '#x'})
context_dec = simple_context({'int': 'd'})


@pytest.mark.parametrize(['value', 'context', 'expected'], [
    pytest.param(Int(1024), context_hex, '0x400', id='pos hex'),
    pytest.param(Int(1024), context_dec, '1024', id='pos dec'),
])
def test_text(value, context, expected):
    assert value.text(context) == expected


@pytest.mark.parametrize(['name', 'value', 'expected'], [
    pytest.param(Name('int'), Int(1024), '"int":i = 1024', id='pos dec'),
    pytest.param(Name('int'), Int(-1024), '"int":i = -1024', id='neg dec'),
])
def test_serialize_pair_dec(name, value, expected):
    stream = StringIO()
    context_dec['fst'] = True
    serialize_pair(name, value, stream, lambda t: None, 0, context_dec)
    assert stream.getvalue() == expected
