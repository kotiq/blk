import pytest
from blk.types import BlockComment, CloneLast, Include, LineComment, Name, Override, Str


samples = {
    'include': {
        None: Include('relative/path'),
        'name': Name('@include'),
        'value': Str('relative/path'),
        'repr': "Include('relative/path')",
    },
    'line_comment': {
        None: LineComment('line comment'),
        'name': Name('@commentCPP'),
        'value': Str('line comment'),
        'repr': "LineComment('line comment')",
    },
    'block_comment': {
        None: BlockComment('block\ncomment'),
        'name': Name('@commentC'),
        'value': Str('block\ncomment'),
        'repr': r"BlockComment('block\ncomment')"
    },
    'override': {
        None: Override('target', Str('value')),
        'name': Name('@override:target'),
        'value': Str('value'),
        'repr': "Override('target', Str('value'))",
        'target': Name('target'),
    },
    'clone_last': {
        None: CloneLast('target', Str('value')),
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
        name = base if suffix is None else f'{base}_{suffix}'
        globals()[name] = make_fixture(value)
