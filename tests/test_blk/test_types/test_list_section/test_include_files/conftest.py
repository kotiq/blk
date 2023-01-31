from pytest import fixture
from blk.types import Int, ListSection
from blk.text import serialize
from helpers import make_tmppath

tmppath = make_tmppath(__name__)


@fixture(scope='module')
def list_section_without_includes():
    root = ListSection()
    root.add('int', Int(42))
    root.add('zero', Int(0))
    sub = ListSection()
    sub.add('three', Int(3))
    sub.add('four', Int(4))
    sub.add('five', Int(5))
    root.add('sub', sub)
    root.add('one', Int(1))
    root.add('two', Int(2))
    return root


@fixture(scope='module')
def first_level():
    root = ListSection()
    root.add('int', Int(42))
    return root


@fixture(scope='module')
def list_section_with_first_level_include():
    root = ListSection()
    root.add_include('include/first_level.blk')
    root.add('zero', Int(0))
    sub = ListSection()
    sub.add('three', Int(3))
    sub.add('four', Int(4))
    sub.add('five', Int(5))
    root.add('sub', sub)
    root.add('one', Int(1))
    root.add('two', Int(2))
    return root


@fixture(scope='module')
def second_level():
    root = ListSection()
    root.add('four', Int(4))
    root.add('five', Int(5))
    return root


@fixture(scope='module')
def list_section_with_second_level_include():
    root = ListSection()
    root.add('int', Int(42))
    root.add('zero', Int(0))
    sub = ListSection()
    sub.add('three', Int(3))
    sub.add_include('include/second_level.blk')
    root.add('sub', sub)
    root.add('one', Int(1))
    root.add('two', Int(2))
    return root


@fixture(scope='module')
def first_level_nested():
    root = ListSection()
    root.add_include('first_level.blk')
    root.add_include('nested/nested.blk')
    return root


@fixture(scope='module')
def nested():
    root = ListSection()
    root.add('zero', Int(0))
    return root


@fixture(scope='module')
def list_section_with_nested_include():
    root = ListSection()
    root.add_include('include/first_level_nested.blk')
    sub = ListSection()
    sub.add('three', Int(3))
    sub.add_include('include/second_level.blk')
    root.add('sub', sub)
    root.add('one', Int(1))
    root.add('two', Int(2))
    return root


@fixture(scope='module')
def file_first_level(first_level, tmppath):
    path = tmppath / 'include' / 'first_level.blk'
    path.parent.mkdir(exist_ok=True)
    with open(path, 'w') as ostream:
        serialize(first_level, ostream)
    return path


@fixture(scope='module')
def file_with_first_level_include(list_section_with_first_level_include, file_first_level, tmppath):
    path = tmppath / 'with_first_level_include.blk'
    with open(path, 'w') as ostream:
        serialize(list_section_with_first_level_include, ostream)
    return path


@fixture(scope='module')
def file_second_level(second_level, tmppath):
    path = tmppath / 'include' / 'second_level.blk'
    path.parent.mkdir(exist_ok=True)
    with open(path, 'w') as ostream:
        serialize(second_level, ostream)
    return path


@fixture(scope='module')
def file_with_second_level_include(list_section_with_second_level_include, file_second_level, tmppath):
    path = tmppath / 'with_second_level_include.blk'
    with open(path, 'w') as ostream:
        serialize(list_section_with_second_level_include, ostream)
    return path


@fixture(scope='module')
def file_nested(nested, tmppath):
    path = tmppath / 'include' / 'nested' / 'nested.blk'
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as ostream:
        serialize(nested, ostream)
    return path


@fixture(scope='module')
def file_first_level_nested(first_level_nested, file_first_level, file_nested, tmppath):
    path = tmppath / 'include' / 'first_level_nested.blk'
    path.parent.mkdir(exist_ok=True)
    with open(path, 'w') as ostream:
        serialize(first_level_nested, ostream)
    return path


@fixture(scope='module')
def file_with_nested_include(list_section_with_nested_include, file_first_level_nested, file_second_level, tmppath):
    path = tmppath / 'with_nested_include.blk'
    with open(path, 'w') as ostream:
        serialize(list_section_with_nested_include, ostream)
    return path


@fixture(scope='module')
def file_without_includes(list_section_without_includes, tmppath):
    path = tmppath / 'without_includes.blk'
    with open(path, 'w') as ostream:
        serialize(list_section_without_includes, ostream)
    return path

