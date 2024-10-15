from pytest import fixture
from blk.types import ListSection


@fixture
def empty():
    return ListSection()
