from pytest import fixture
from pytest_lazyfixture import lazy_fixture
from blk.types import DictSection, Int, ListSection, Name


@fixture(scope='module')
def list_section():
    return ListSection([
        (Name('a'), ListSection([(Name('x'), Int(1))])),
        (Name('a'), ListSection([(Name('y'), Int(2))])),
        (Name('b'), ListSection([(Name('x'), Int(1))])),
        (Name('b'), ListSection([(Name('y'), Int(2))])),
        (Name('x'), Int(1))
    ])


@fixture(scope='module')
def dict_section():
    return DictSection([
        (Name('a'), [
            DictSection([(Name('x'), [Int(1)])]),
            DictSection([(Name('y'), [Int(2)])]),
        ]),
        (Name('b'), [
            DictSection([(Name('x'), [Int(1)])]),
            DictSection([(Name('y'), [Int(2)])]),
        ]),
        (Name('c'), [Int(1)]),
    ])


@fixture(scope='module', params=lazy_fixture(['list_section', 'dict_section']))
def section(request):
    return request.param
