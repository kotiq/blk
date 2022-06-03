from itertools import product, chain
import pytest
from pytest_lazyfixture import lazy_fixture


_ = globals().__getitem__


def inject_lazy(name):
    globals()[name] = lazy_fixture(name)


bases = 'include', 'line_comment', 'block_comment', 'override'
suffixes = 'name', 'value', 'repr'

for fixture_name in chain(bases, ('_'.join(p) for p in product(bases, suffixes))):
    inject_lazy(fixture_name)

aliases = {
    'include': ('value', 'path'),
    'line_comment': ('value', 'text'),
    'block_comment': ('value', 'text'),
}


@pytest.mark.parametrize(['item', 'attr_name', 'attr_value'], [
    pytest.param(_(base), attr_name, _(f'{base}_{attr_name}'), id=f'{base}-{attr_name}')
    for base in bases
    for attr_name in ('name', 'value')
])
def test_attr(item, attr_name, attr_value):
    assert getattr(item, attr_name) == attr_value


@pytest.mark.parametrize(['item', 'item_repr'], [
    pytest.param(_(base), _(f'{base}_repr'), id=f'{base}-repr') for base in bases
])
def test_repr(item, item_repr):
    assert repr(item) == item_repr


@pytest.mark.parametrize(['item', 'attr_names'], [
    pytest.param(_(base), aliases[base], id='-'.join((base, *aliases[base]))) for base in bases
    if base in aliases
])
def test_alias(item, attr_names):
    a, b = (getattr(item, n) for n in attr_names)
    assert a == b
