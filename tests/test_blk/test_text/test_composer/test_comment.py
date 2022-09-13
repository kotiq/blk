import pytest
from pytest import param as _
from blk.types import LineComment, BlockComment
from blk.text.composer import comment


@pytest.mark.parametrize(['text', 'item'], [
    _('//line comment', LineComment('line comment'), id='line'),
    _('// line comment', LineComment('line comment'), id='line after spase'),
    _('/*block\ncomment*/', BlockComment('block\ncomment'), id='block'),
    _('/*\nblock\ncomment\n*/', BlockComment('block\ncomment'), id='block inside newlines'),
])
def test_comment(text, item):
    parsed = comment.parse(text)
    assert isinstance(parsed, item.__class__)
    assert parsed == item
