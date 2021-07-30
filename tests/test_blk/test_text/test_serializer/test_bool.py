from io import StringIO
import pytest
from blk.types import Name, true, false
from blk.text.serializer import serialize_pair
from . import simple_context


context_alg = simple_context({'false': '0', 'true': '1', })
context_log = simple_context({'false': 'false', 'true': 'true'})


@pytest.mark.parametrize(['value', 'context', 'expected'], [
    pytest.param(true, context_alg, '1', id='true log'),
    pytest.param(false, context_alg, '0', id='false log'),
    pytest.param(true, context_log, 'true', id='true alg'),
    pytest.param(false, context_log, 'false', id='false alg')
])
def test_text(value, context, expected):
    assert value.text(context) == expected


@pytest.mark.parametrize(['name', 'value', 'expected'], [
    pytest.param(Name('bool'), true, '"bool":b = true', id='true log'),
    pytest.param(Name('bool'), false, '"bool":b = false', id='false log'),
])
def test_serialize_pair_log(name, value, expected):
    stream = StringIO()
    context_log['fst'] = True
    serialize_pair(name, value, stream, lambda t: None, 0, context_log)
    assert stream.getvalue() == expected
