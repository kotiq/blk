import pytest
from blk.types import *


@pytest.fixture()
def section():
    root = Section()
    names = 'abcderfghijkl'

    def parameter_name(n):
        return f'{n}1'

    sections_map = {t: Section() for t in names}
    parameters_map = {parameter_name(t): Str(parameter_name(t)) for t in names}
    adjacency_list = {
        None: 'abc',
        'a': 'def',
        'b': 'ghi',
        'c': 'jkl',
    }
    for v, vs in adjacency_list.items():
        section_ = root if v is None else sections_map[v]
        for n in vs:
            section_.add(n, sections_map[n])
            section_.add(parameter_name(n), parameters_map[parameter_name(n)])

    return root


def maybe_str(t):
    return t if t is None else str(t)


def ans(ps):
    return [maybe_str(p[0]) for p in ps if p is not Section.end]


def test_sorted_pairs(section: Section):
    sorted_pairs = ans(section.sorted_pairs())
    assert sorted_pairs == ['a1', 'b1', 'c1', 'a', 'b', 'c']


def test_bfs_pairs(section: Section):
    all_names = ans(section.bfs_sorted_pairs())
    assert all_names == [
        None,
        'a1', 'b1', 'c1', 'a', 'b', 'c',
        'd1', 'e1', 'f1', 'd', 'e', 'f',
        'g1', 'h1', 'i1', 'g', 'h', 'i',
        'j1', 'k1', 'l1', 'j', 'k', 'l'
    ]


def test_dfs_nlr_pairs(section: Section):
    all_names = ans(section.dfs_nlr_pairs())
    assert all_names == [
        None,
        'a',
        'd', 'd1', 'e', 'e1', 'f', 'f1', 'a1',
        'b',
        'g', 'g1', 'h', 'h1', 'i', 'i1', 'b1',
        'c',
        'j', 'j1', 'k', 'k1', 'l', 'l1', 'c1'
    ]


def test_names_dfs_nlr(section: Section):
    names = list(map(maybe_str, section.names()))
    assert names == [
        'a',
        'd', 'd1', 'e', 'e1', 'f', 'f1', 'a1',
        'b',
        'g', 'g1', 'h', 'h1', 'i', 'i1', 'b1',
        'c',
        'j', 'j1', 'k', 'k1', 'l', 'l1', 'c1'
    ]
