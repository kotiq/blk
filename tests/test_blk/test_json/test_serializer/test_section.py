import pytest
from pytest import param as _
from pytest_lazyfixture import lazy_fixture
from blk.format_ import Format
from blk.json.serializer import serialize

get = globals().__getitem__

names = (
    'json',
    'json_2',
    'json_3',
)
for name in names:
    globals()[name] = lazy_fixture(name)

def _test_json_like(generated, expected):
    generated = generated.replace(', \n', ',\n')
    assert generated == expected

@pytest.mark.parametrize(['out_type', 'text'], [_(Format[n.upper()], get(n), id=n) for n in names])
def test_serialize(ostream, dict_section, out_type, text):
    serialize(dict_section, ostream, out_type)
    ostream.seek(0)
    _test_json_like(ostream.read(), text)
