from pytest import fixture
from pytest_lazyfixture import lazy_fixture
from blk.types import DictSection, Float, Int, ListSection, Name


@fixture(scope='module')
def list_section():
    return ListSection([
        (Name('x'), Int(1)),
        (Name('x'), Int(2)),
        (Name('y'), Float(1.0)),
        (Name('y'), Float(2.0)),
    ])


@fixture(scope='module')
def dict_section():
    return DictSection([
        (Name('x'), [Int(1), Int(2)]),
        (Name('y'), [Float(1.0), Float(1.0)]),
    ])


@fixture(scope='module', params=lazy_fixture(['list_section', 'dict_section']))
def section(request):
    return request.param
