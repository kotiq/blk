from pytest import fixture
from blk.types import DictSection, Int, ListSection, Name


@fixture(scope='module')
def list_section_source():
    return ListSection([
        (Name('x'), Int(1)),
        (Name('inner'), ListSection([
            (Name('y'), Int(3))
        ])),
        (Name('x'), Int(2)),
    ])


@fixture(scope='module')
def dict_section_target():
    return DictSection([
        (Name('x'), [Int(1), Int(2)]),
        (Name('inner'), [DictSection([
            (Name('y'), [Int(3)]),
        ])])
    ])


@fixture(scope='module')
def dict_section_source():
    return DictSection([
        (Name('x'), [Int(1), Int(2)]),
        (Name('inner'), [DictSection([
            (Name('y'), [Int(3)]),
        ])])
    ])


@fixture(scope='module')
def list_section_target():
    return ListSection([
        (Name('x'), Int(1)),
        (Name('x'), Int(2)),
        (Name('inner'), ListSection([
            (Name('y'), Int(3))
        ])),
    ])
