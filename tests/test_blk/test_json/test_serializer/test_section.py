import pytest
from pytest import param as _
from pytest_lazyfixture import lazy_fixture
from blk.json.serializer import serialize, JSON, JSON_2, JSON_3

get = globals().__getitem__
formats = {
    'json': JSON,
    'json_2': JSON_2,
    'json_3': JSON_3,
}

for fixture_name in formats:
    globals()[fixture_name] = lazy_fixture(fixture_name)

test_serialize_params = [_(formats[fmt], get(fmt), id=fmt) for fmt in formats]


@pytest.mark.parametrize(['out_type', 'text'], test_serialize_params)
def test_serialize(ostream, dict_section, out_type, text):
    serialize(dict_section, ostream, out_type)
    ostream.seek(0)
    assert ostream.read() == text

