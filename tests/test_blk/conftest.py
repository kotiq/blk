import pytest
from blk.types import (Color, DictSection, Float, Float2, Float3, Float4, Float12, Int, Int2, Int3, Long, Str, false,
                       true)


@pytest.fixture(scope='session')
def mixed_dict_section():
    """Секция со всеми типами значений."""

    root = DictSection()
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

    inner = DictSection()
    inner.add('a', Int(1))
    inner.add('b', Long(2))
    root.add('inner', inner)
    return root


@pytest.fixture(scope='session')
def dict_sections_only_dict_section():
    """DictSection только из секций."""

    root = DictSection()
    alpha = DictSection()
    beta = DictSection()
    root.add('alpha', alpha)
    root.add('beta', beta)
    return root


@pytest.fixture(scope='session')
def expected_names():
    return 'scalar', 'section', 'scalar', 'section', 'scalar'


@pytest.fixture(scope='session')
def dict_section_with_cycle():
    """DictSection с циклом.
    Для вывода текста нижние уровни не должны содержать ссылки из верхних уровней."""

    root = DictSection()
    root.add('scalar', Int(42))
    root.add('section', root)
    return root


@pytest.fixture(scope='session')
def dict_section_with_same_id_sub():
    """DictSection с идентичной подсекцией на одном уровне.
    Для вывода текста одинаковые ссылки на одном уровне допустимы."""

    root = DictSection()
    sub = DictSection()
    sub.add('scalar', Int(42))
    root.add('sub1', sub)
    root.add('sub2', sub)
    return root


@pytest.fixture(scope='session')
def dict_section_with_cycle_deep():
    """DictSection с идентичными подсекциями через уровень."""

    root = DictSection()
    root.add('scalar', Int(42))
    sub = DictSection()
    sub.add('scalar', Int(42))
    sub.add('section', root)
    root.add('section', sub)
    return root


@pytest.fixture(scope='session')
def dict_section_with_same_id_sub_deep():
    """DictSection с идентичными подсекциями на уровне с разными родителями."""

    root = DictSection()
    sub = DictSection()
    sub.add('scalar', Int(42))
    inter1 = DictSection()
    inter1.add('sub', sub)
    inter2 = DictSection()
    inter2.add('sub', sub)
    root.add('inter1', inter1)
    root.add('inter2', inter2)
    return root
