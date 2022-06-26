from itertools import product, chain
import pytest
from pytest import param as _
from pytest_lazyfixture import lazy_fixture

get = globals().__getitem__
bases = 'override', 'clone_last'
suffixes = ('target', )

for fixture_name in chain(bases, ('_'.join(p) for p in product(bases, suffixes))):
    globals()[fixture_name] = lazy_fixture(fixture_name)

test_target_params = [_(get(base), get(f'{base}_target'), id=base) for base in bases]


@pytest.mark.parametrize(['item', 'item_target'], test_target_params)
def test_target(item, item_target):
    assert item.target == item_target
