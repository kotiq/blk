from itertools import product, chain
import pytest
from pytest_lazyfixture import lazy_fixture


_ = globals().__getitem__


def inject_lazy(name):
    globals()[name] = lazy_fixture(name)


bases = 'override', 'clone_last'
suffixes = ('target', )

for fixture_name in chain(bases, ('_'.join(p) for p in product(bases, suffixes))):
    inject_lazy(fixture_name)


@pytest.mark.parametrize(['item', 'item_target'], [
    pytest.param(_(base), _(f'{base}_target'), id=base) for base in bases
])
def test_target(item, item_target):
    assert item.target == item_target
