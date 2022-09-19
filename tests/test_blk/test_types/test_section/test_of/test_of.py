from pytest import mark, param as _
from pytest_lazyfixture import lazy_fixture


@mark.parametrize(['source', 'target'], [
    _(*lazy_fixture(['list_section_source', 'dict_section_target']), id='list to dict'),
    _(*lazy_fixture(['dict_section_source', 'list_section_target']), id='dict to list'),
])
def test_of(source, target):
    assert target.of(source) == target
