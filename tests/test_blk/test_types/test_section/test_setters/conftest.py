from pytest import fixture
from blk.types import DictSection, ListSection


@fixture(params=[
    DictSection,
    ListSection,
], ids=lambda t: t.__name__)
def empty_factory(request):
    return request.param
