from pytest import fixture
from blk.types import DictSection


@fixture
def empty():
    return DictSection()
