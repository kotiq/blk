from io import StringIO
import pytest
from blk.types import Name, Float
from blk.text.serializer import serialize_pair
from . import simple_context


context_exp = simple_context({'float': '.7e'})
context_gen = simple_context({'float': '.7g'})


@pytest.mark.parametrize(['value', 'context', 'expected'], [
    pytest.param(Float(12345.6789), context_exp, '1.2345679e+04', id='pos exp'),
    pytest.param(Float(12345.6789), context_gen, '12345.68', id='pos gen'),
])
def test_text(value, context, expected):
    assert value.text(context) == expected


@pytest.mark.parametrize(['name', 'value', 'expected'], [
    pytest.param(Name('float'), Float(12345.6789), '"float":r = 12345.68', id='pos gen'),
    pytest.param(Name('float'), Float(-12345.6789), '"float":r = -12345.68', id='neg gen'),
])
def test_serialize_pair_gen(name, value, expected):
    stream = StringIO()
    context_gen['fst'] = True
    serialize_pair(name, value, stream, lambda t: None, 0, context_gen)
    assert stream.getvalue() == expected
