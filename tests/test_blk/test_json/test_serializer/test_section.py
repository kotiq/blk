import pytest
from pytest import param as _
from pytest_lazyfixture import lazy_fixture
from blk.format import Format
from blk.json.serializer import serialize

get = globals().__getitem__

names = ('json', 'json_2', 'json_3')
for name in names:
    globals()[name] = lazy_fixture(name)


@pytest.mark.parametrize(['out_type', 'text'], [_(Format[n.upper()], get(n), id=n) for n in names])
def test_serialize(ostream, dict_section, out_type, text):
    serialize(dict_section, ostream, out_type)
    ostream.seek(0)
    assert ostream.read() == text
