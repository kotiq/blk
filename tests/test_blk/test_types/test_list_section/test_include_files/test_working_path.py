from pytest import mark, param
from pytest_lazyfixture import lazy_fixture
from blk.text import compose_file


def _(*names, id):
    return param(*lazy_fixture(names), id=id)


@mark.parametrize(['sample', 'expected'], [
    _('file_without_includes', 'list_section_without_includes', id='without includes'),
    _('file_with_first_level_include', 'list_section_without_includes', id='first level include'),
    _('file_with_second_level_include', 'list_section_without_includes', id='second level include'),
    _('file_with_nested_include', 'list_section_without_includes', id='nested include'),
])
def test_compose(sample, expected):
    assert compose_file(sample, remove_comments=False, include_files=True) == expected
