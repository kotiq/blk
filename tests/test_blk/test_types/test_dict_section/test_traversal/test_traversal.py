def maybe_str(t):
    return t if t is None else str(t)


def names(ps):
    return [maybe_str(p[0]) for p in ps]


def test_sorted_pairs(dict_section, sorted_pairs_names):
    assert names(dict_section.sorted_pairs()) == sorted_pairs_names


def test_bfs_pairs(dict_section, bfs_sorted_pairs_names):
    assert names(dict_section.bfs_sorted_pairs()) == bfs_sorted_pairs_names


def test_names_dfs_nlr(dict_section, dfs_nlr_names):
    assert list(map(maybe_str, dict_section.names())) == dfs_nlr_names
