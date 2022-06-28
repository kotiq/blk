import pytest
from blk.types import DictSection, Float, Int


@pytest.fixture(scope='module')
def single_map():
    root = DictSection()
    root.add('a', Int(1))
    root.add('b', Int(2))
    root.add('c', Int(3))
    sub = DictSection()
    sub.add('x', Float(4))
    sub.add('y', Float(5))
    root.add('sub', sub)
    return root


@pytest.fixture(scope='module')
def multi_map():
    root = DictSection()
    root.add('a', Int(1))
    root.add('a', Int(2))
    root.add('b', Int(3))
    sub = DictSection()
    sub.add('x', Float(4))
    sub.add('y', Float(5))
    root.add('sub', sub)
    return root
