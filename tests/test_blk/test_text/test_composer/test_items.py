from pytest import mark, param as _
from blk.types import (Float, Int, ListSection, Name, Str)
from blk.text.composer import items
from test_blk.test_text.test_composer.test_item import like

@mark.parametrize(['text', 'items_'], [
    _('', ListSection(), id='empty'),
    _('"int":i = 42',
      ListSection([(Name('int'), Int(42))]), id='single'),
    _('"int":i=42; "float":r = 4.2',
      ListSection([(Name('int'), Int(42)), (Name('float'), Float(4.2))]), id='pair single line'),
    _('"int":i=42\n"float":r = 4.2',
      ListSection([(Name('int'), Int(42)), (Name('float'), Float(4.2))]), id='pair two lines'),
    _('//cpp comment\n"int":i = 42',
      ListSection([(Name('@commentCPP'), Str('cpp comment')), (Name('int'), Int(42))]), id='single cpp comment'),
    _('/*c\ncomment*/\n"int":i = 42',
      ListSection([(Name('@commentC'), Str('c\ncomment')), (Name('int'), Int(42))]), id='single c comment'),
    _('include file.blk\n"int":i = 42',
      ListSection([(Name('@include'), Str('file.blk')), (Name('int'), Int(42))]), id='include'),
])
def test_compose_items(text, items_):
    parsed = items.parse(text)
    assert isinstance(parsed, ListSection)
    assert all(like(p, q) for p, q in zip(parsed.pairs(), items_.pairs()))
