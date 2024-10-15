from pytest import mark, param
from pytest_lazyfixture import lazy_fixture
from blk.text import compose_file


def _(*names, id_):
    return param(*lazy_fixture(names), id=id_)


@mark.parametrize(['sample', 'expected'], [
    _('file_without_includes', 'list_section_without_includes', id_='without includes'),
    _('file_with_first_level_include', 'list_section_without_includes', id_='first level include'),
    _('file_with_second_level_include', 'list_section_without_includes', id_='second level include'),
    _('file_with_nested_include', 'list_section_without_includes', id_='nested include'),
])
def test_compose(sample, expected):
    assert compose_file(sample, remove_comments=False, include_files=True) == expected
