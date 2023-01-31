from pytest import fixture
from blk.types import Int, ListSection


@fixture(scope='module')
def list_section_without_comments():
    root = ListSection()
    root.add('int', Int(42))
    root.add('zero', Int(0))
    sub = ListSection()
    root.add('one', Int(1))
    root.add('two', Int(2))
    root.add('sub', sub)
    return root


@fixture(scope='module')
def list_section_with_comments():
    root = ListSection()
    root.add_comment('line comment')
    root.add('int', Int(42))
    root.add_comment('another line comment')
    root.add('zero', Int(0))
    sub = ListSection()
    sub.add_comment('begin\nsubsection')
    root.add('one', Int(1))
    sub.add_comment('line comment')
    root.add('two', Int(2))
    sub.add_comment('end\nsubsection')
    root.add('sub', sub)
    return root
