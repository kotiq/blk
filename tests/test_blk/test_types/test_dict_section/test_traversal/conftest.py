import pytest
from blk.types import DictSection, Str


@pytest.fixture(scope='session')
def dict_section():
    root = DictSection()
    names = 'abcderfghijkl'

    def parameter_name(n):
        return f'{n}1'

    sections_map = {t: DictSection() for t in names}
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


@pytest.fixture(scope='module')
def sorted_pairs_names():
    return ['a1', 'b1', 'c1', 'a', 'b', 'c']


@pytest.fixture(scope='module')
def bfs_sorted_pairs_names():
    return [
        None,
        'a1', 'b1', 'c1', 'a', 'b', 'c',
        'd1', 'e1', 'f1', 'd', 'e', 'f',
        'g1', 'h1', 'i1', 'g', 'h', 'i',
        'j1', 'k1', 'l1', 'j', 'k', 'l'
    ]


@pytest.fixture(scope='module')
def dfs_nlr_names():
    return [
        'a',
        'd', 'd1', 'e', 'e1', 'f', 'f1', 'a1',
        'b',
        'g', 'g1', 'h', 'h1', 'i', 'i1', 'b1',
        'c',
        'j', 'j1', 'k', 'k1', 'l', 'l1', 'c1'
    ]
