import pytest
from blk.types import false, true


@pytest.mark.parametrize(['value', 'text'], [
    pytest.param(false, 'false', id='false'),
    pytest.param(true, 'true', id='true'),
])
def test_repr(value, text):
    assert repr(value) == text
    assert eval(text) is value
