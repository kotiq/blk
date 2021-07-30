from io import StringIO
import pytest
from blk.types import Name, true, false, Section
from blk.text.serializer import serialize_pair, serialize_pairs
from . import simple_context


default_context = simple_context({
    'false': 'off', 'true': 'on',
    'name_type_sep': ':',
    'type_value_sep': ' = ',
    'name_opener_sep': ' ',
    'sec_opener': '',
})


def make_nested_section():
    value = Section()
    value.append(Name('bool'), false)
    value.append(Name('bool'), true)
    sub = Section()
    sub.append(Name('bool'), false)
    sub.append(Name('bool'), true)
    value.append(Name('sub'), sub)
    value.append(Name('true'), true)
    return value


nested_section = make_nested_section()

empty_section_pair_text_default = """\
"section" {
}\
"""

nested_section_pair_text_default = """\
"section" {
  "bool":b = off
  "bool":b = on
  "sub" {
    "bool":b = off
    "bool":b = on
  }
  "true":b = on
}\
"""


@pytest.mark.parametrize(['name', 'value', 'expected', 'context'], [
    pytest.param(Name('section'), Section(), empty_section_pair_text_default, default_context,
                 id='empty section pair default'),
    pytest.param(Name('section'), nested_section, nested_section_pair_text_default, default_context,
                 id='nested section pair default'),
])
def test_serialize_pair(name, value, expected, context):
    stream = StringIO()

    def indent(n):
        stream.write(' '*2*n)

    context['fst'] = True
    serialize_pair(name, value, stream, indent, 0, context)
    assert stream.getvalue() == expected


nested_section_text_default = """\
"bool":b = off
"bool":b = on
"sub" {
  "bool":b = off
  "bool":b = on
}
"true":b = on\
"""


@pytest.mark.parametrize(['section', 'expected', 'context'], [
    pytest.param(nested_section, nested_section_text_default, default_context, id='nested default'),
])
def test_serialize_pairs(section, expected, context):
    stream = StringIO()

    def indent(n):
        stream.write(' '*2*n)

    context['fst'] = True
    serialize_pairs(section.pairs(), stream, indent, 0, context)
    assert stream.getvalue() == expected
