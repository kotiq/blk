from pytest import mark, param
from pytest_lazyfixture import lazy_fixture


def _(*names, id):
    return param(*lazy_fixture(names), id=id)


@mark.parametrize(['sample', 'expected'], [
    _('list_section_without_comments', 'list_section_without_comments', id='without comments'),
    _('list_section_with_comments', 'list_section_without_comments', id='with comments'),
])
def test_remove_comments(sample, expected):
    sample.remove_comments()
    assert sample == expected
