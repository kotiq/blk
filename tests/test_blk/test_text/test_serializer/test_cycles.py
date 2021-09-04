import io
import itertools as itt
import pytest
from pytest_lazyfixture import lazy_fixture
from blk.types import *
import blk.text as txt


@pytest.fixture(scope='module')
def section_with_cycle():
    """Для вывода текста нижние урони не должны содержать ссылки из верхних уровней."""

    root = Section()
    root.add('scalar', Int(42))
    root.add('section', root)
    return root


@pytest.fixture(scope='module')
def section_with_same_id_sub():
    """Для вывода текста одинаковые ссылки на одном уровне допустимы."""

    root = Section()
    sub = Section()
    sub.add('scalar', Int(42))
    root.add('sub1', sub)
    root.add('sub2', sub)
    return root


@pytest.fixture(scope='module')
def section_with_cycle_deep():
    root = Section()
    root.add('scalar', Int(42))
    sub = Section()
    sub.add('scalar', Int(42))
    sub.add('section', root)
    root.add('section', sub)
    return root


@pytest.fixture(scope='module')
def section_with_same_id_sub_deep():
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


section_with_same_id_sub_text = """\
"sub1" {
  "scalar":i = 42
}
"sub2" {
  "scalar":i = 42
}
"""

expected_some_name = ['scalar', 'section', 'scalar', 'section', 'scalar']


def test_section_with_cycle_sample(section_with_cycle: Section):
    some_pairs_it = itt.islice(section_with_cycle.names(), 0, 5)
    some_names = list(str(p) for p in some_pairs_it)
    assert some_names == expected_some_name


@pytest.mark.parametrize(['section', 'has_cycle'], [
    pytest.param(lazy_fixture('section_with_cycle'), True, id='section with cycle'),
    pytest.param(lazy_fixture('section_with_same_id_sub'), False, id='section_with_same_id_sub'),
    pytest.param(lazy_fixture('section_with_cycle_deep'), True, id='section_with_cycle_deep'),
    pytest.param(lazy_fixture('section_with_same_id_sub_deep'), False, id='section_with_same_id_sub_deep'),
])
def test_cycle(section: Section, has_cycle: bool):
    if has_cycle:
        with pytest.raises(CycleError):
            section.check_cycle()
    else:
        section.check_cycle()


def test_section_with_same_id_sub(section_with_same_id_sub: Section):
    stream = io.StringIO()
    txt.serialize(section_with_same_id_sub, stream)
    text = stream.getvalue()
    assert text == section_with_same_id_sub_text


def test_section_with_cycle(section_with_cycle: Section):
    stream = io.StringIO()
    with pytest.raises(CycleError):
        txt.serialize(section_with_cycle, stream)
