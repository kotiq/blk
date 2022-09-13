from pytest import mark, raises, param as _
import parsy as ps
from blk.types import Int, ListSection, Name, Str
from blk.text.composer import named_value


@mark.parametrize(['text', 'value'], [
    _('"int" : i = 42', [Name('int'), Int(42)], id='no ignored comment'),
    _('"int" /*comment*/ : i = 42', [Name('int'), Int(42)], id='ignored comment after name'),
    _('"int": /*comment*/ i = 42', [Name('int'), Int(42)], id='ignored comment after colon'),
    _('"int":i /*comment*/ = 42', [Name('int'), Int(42)], id='ignored comment after tag'),
    _('"int":i = /*comment*/ 42', [Name('int'), Int(42)], id='ignored comment after equals'),
])
def test_named_parameter(text, value):
    parsed = named_value.parse(text)
    assert isinstance(parsed, list)
    assert parsed == value
