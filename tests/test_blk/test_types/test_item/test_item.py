from itertools import product, chain
import pytest
from pytest import param as _
from pytest_lazyfixture import lazy_fixture


get = globals().__getitem__
bases = 'include', 'line_comment', 'block_comment', 'override'
suffixes = 'name', 'value', 'repr'

for fixture_name in chain(bases, ('_'.join(p) for p in product(bases, suffixes))):
    globals()[fixture_name] = lazy_fixture(fixture_name)

aliases = {
    'include': ('value', 'path'),
    'line_comment': ('value', 'text'),
    'block_comment': ('value', 'text'),
}

test_attr_params = [
    _(get(base), attr_name, get(f'{base}_{attr_name}'), id=f'{base}-{attr_name}')
    for base in bases
    for attr_name in ('name', 'value')
]


@pytest.mark.parametrize(['item', 'attr_name', 'attr_value'], test_attr_params)
def test_attr(item, attr_name, attr_value):
    assert getattr(item, attr_name) == attr_value


test_repr_params = [_(get(base), get(f'{base}_repr'), id=f'{base}-repr') for base in bases]


@pytest.mark.parametrize(['item', 'item_repr'], test_repr_params)
def test_repr(item, item_repr):
    assert repr(item) == item_repr


test_alias_params = [_(get(base), aliases[base], id='-'.join((base, *aliases[base]))) for base in bases
                     if base in aliases]


@pytest.mark.parametrize(['item', 'attr_names'], test_alias_params)
def test_alias(item, attr_names):
    a, b = (getattr(item, n) for n in attr_names)
    assert a == b
