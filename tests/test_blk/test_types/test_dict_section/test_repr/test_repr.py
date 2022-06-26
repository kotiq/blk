import pytest
from pytest import param as _
from pytest_lazyfixture import lazy_fixture
from blk.types import DictSection, Float2, Float3, Name, Str

params = [_(*lazy_fixture([f'{t}_dict_section', f'{t}_dict_section_text']), id=t) for t in ('flat', 'nested')]


@pytest.mark.parametrize(['value', 'text'], params)
def test_repr_dict_section(value, text):
    assert repr(value) == text
    assert eval(text) == value
