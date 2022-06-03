import pytest
from blk.types import Name, Str, Include, LineComment, BlockComment, Override, CloneLast


samples = {
    'include': {
        '': Include('relative/path'),
        'name': Name('@include'),
        'value': Str('relative/path'),
        'repr': "Include('relative/path')",
    },
    'line_comment': {
        '': LineComment('line comment'),
        'name': Name('@commentCPP'),
        'value': Str('line comment'),
        'repr': "LineComment('line comment')",
    },
    'block_comment': {
        '': BlockComment('block\ncomment'),
        'name': Name('@commentC'),
        'value': Str('block\ncomment'),
        'repr': r"BlockComment('block\ncomment')"
    },
    'override': {
        '': Override('target', Str('value')),
        'name': Name('@override:target'),
        'value': Str('value'),
        'repr': "Override('target', Str('value'))",
        'target': Name('target'),
    },
    'clone_last': {
        '': CloneLast('target', Str('value')),
        'name': Name('@clone-last:target'),
        'value': Str('value'),
        'repr': "CloneLast('target', Str('value'))",
        'target': Name('target'),
    },
}


def make_fixture(v):
    @pytest.fixture(scope='module')
    def f():
        return v
    return f


for base, m in samples.items():
    for suffix, value in m.items():
        name = f'{base}_{suffix}' if suffix else base
        globals()[name] = make_fixture(value)
