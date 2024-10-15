from pytest import fixture
from blk.types import Int, ListSection, Name, Str


@fixture
def empty():
    return ListSection()


@fixture
def section_oneline_param():
    return ListSection([
        (Name('int'), Int(42)),
    ])


@fixture
def section_oneline_param_with_line_comment():
    return ListSection([
        (Name('int'), Int(42)),
        (Name('@commentCPP'), Str('integer')),
    ])

