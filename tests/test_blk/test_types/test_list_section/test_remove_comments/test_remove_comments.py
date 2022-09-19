from pytest import mark, param as _
from pytest_lazyfixture import lazy_fixture


@mark.parametrize(['sample', 'expected'], [
    _(*lazy_fixture(['list_section_without_comments', 'list_section_without_comments']), id='without comments'),
    _(*lazy_fixture(['list_section_with_comments', 'list_section_without_comments']), id='with comments'),
])
def test_remove_comments(sample, expected):
    sample.remove_comments()
    assert sample == expected
