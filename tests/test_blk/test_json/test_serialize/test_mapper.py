from pprint import pprint
import pytest
from blk.json.serializer import JSON2Mapper, JSONMapper


@pytest.mark.parametrize(['section', 'expected'], [
    pytest.param({}, [], id='empty'),
    pytest.param({'a': [1]}, {'a': [1]}, id='single param'),
    pytest.param({'a': [1], 'b': [2]}, {'a': [1], 'b': [2]}, id='single params'),
    pytest.param({'a': [11, 12]}, {'a': [11, 12]}, id='multi param'),
    pytest.param({'a': [{'b': [1]}]}, {'a': [{'b': [1]}]}, id='single section')
])
def test_json2_map_section(section, expected):
    mapped = JSON2Mapper._map_section(section)
    assert mapped == expected


@pytest.mark.parametrize(['section', 'expected'], [
    pytest.param({}, [], id='empty'),
    pytest.param({'a': [1]}, {'a': 1}, id='single param'),
    pytest.param({'a': [1], 'b': [2]}, {'a': 1, 'b': 2}, id='single params'),
    pytest.param({'a': [11, 12]}, [{'a': 11}, {'a': 12}], id='multi param'),
    pytest.param({'a': [11, 12], 'b': [22]}, [{'a': 11}, {'a': 12}, {'b': 22}], id='mixed before'),
    pytest.param({'a': [11], 'b': [21, 22]}, [{'a': 11}, {'b': 21}, {'b': 22}], id='mixed after'),
    pytest.param({'a': [11], 'b': [21, 22], 'c': [31], 'd': [41, 42]},
                  [{'a': 11}, {'b': 21}, {'b': 22}, {'c': 31}, {'d': 41}, {'d': 42}], id='mixed'),
])
def test_json_map_section(section, expected):
    mapped = JSONMapper._map_section(section)
    pprint(mapped)
    assert mapped == expected
