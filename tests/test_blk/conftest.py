import pytest
from blk.types import *


@pytest.fixture(scope='session')
def mixed_section():
    """Секция со всеми типами значений."""

    root = Section()
    root.add('bool', true)
    root.add('str', Str('hello'))
    root.add('int', Int(0))
    root.add('int', Int(1))
    root.add('long', Int(2))
    root.add('float', Float(3.0))
    root.add('int2', Int2((1, 2)))
    root.add('int3', Int3((1, 2, 3)))
    root.add('color', Color((1, 2, 3, 4)))
    root.add('float2', Float2((1.0, 2.0)))
    root.add('float3', Float3((1.0, 2.0, 3.0)))
    root.add('float4', Float4((1.0, 2.0, 3.0, 4.0)))
    root.add('float12', Float12((
        1.0, 2.0, 3.0,
        4.0, 5.0, 6.0,
        7.0, 8.0, 9.0,
        10.0, 11.0, 12.0,
    )))

    inner = Section()
    inner.add('a', Int(1))
    inner.add('b', Long(2))
    root.add('inner', inner)
    return root


@pytest.fixture(scope='session')
def sections_only_section():
    root = Section()
    alpha = Section()
    beta = Section()
    root.add('alpha', alpha)
    root.add('beta', beta)
    return root


@pytest.fixture(scope='session')
def section_with_cycle():
    """Для вывода текста нижние урони не должны содержать ссылки из верхних уровней."""

    root = Section()
    root.add('scalar', Int(42))
    root.add('section', root)
    return root


@pytest.fixture(scope='session')
def expected_some_names():
    return 'scalar', 'section', 'scalar', 'section', 'scalar'


@pytest.fixture(scope='session')
def section_with_same_id_sub():
    """Для вывода текста одинаковые ссылки на одном уровне допустимы."""

    root = Section()
    sub = Section()
    sub.add('scalar', Int(42))
    root.add('sub1', sub)
    root.add('sub2', sub)
    return root


@pytest.fixture(scope='session')
def section_with_cycle_deep():
    """Секция с одинаковой ссылкой через уровень."""

    root = Section()
    root.add('scalar', Int(42))
    sub = Section()
    sub.add('scalar', Int(42))
    sub.add('section', root)
    root.add('section', sub)
    return root


@pytest.fixture(scope='session')
def section_with_same_id_sub_deep():
    """Секция с одинаковыми ссылками на уровне с разными родителями."""

    root = Section()
    sub = Section()
    sub.add('scalar', Int(42))
    inter1 = Section()
    inter1.add('sub', sub)
    inter2 = Section()
    inter2.add('sub', sub)
    root.add('inter1', inter1)
    root.add('inter2', inter2)
    return root
