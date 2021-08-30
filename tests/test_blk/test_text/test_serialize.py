import io
import sys
import pytest
from blk.types import *
import blk.text as txt


@pytest.fixture(scope='module')
def mixed_section():
    root = Section()
    root.add('bool', true)
    root.add('str', Str('hello'))
    root.add('int', Int(0))
    root.add('int', Int(1))
    root.add('long', Int(2))
    root.add('float', Float(3.0))
    root.add('int2', Int2((1, 2)))
    root.add('int3', Int3((1, 2, 3)))
    root.add('color', Color((1, 2, 3, 4)))
    root.add('float2', Float2((1.0, 2.0)))
    root.add('float3', Float3((1.0, 2.0, 3.0)))
    root.add('float4', Float4((1.0, 2.0, 3.0, 4.0)))
    root.add('float12', Float12((
        1.0, 2.0, 3.0,
        4.0, 5.0, 6.0,
        7.0, 8.0, 9.0,
        10.0, 11.0, 12.0,
    )))

    inner = Section()
    inner.add('a', Int(1))
    inner.add('b', Long(2))
    root.add('inner', inner)
    return root


text_mixed_default = """\
"bool":b = true
"str":t = "hello"
"int":i = 0
"int":i = 1
"long":i = 2
"float":r = 3
"int2":ip2 = 1, 2
"int3":ip3 = 1, 2, 3
"color":c = 0x1, 0x2, 0x3, 0x4
"float2":p2 = 1, 2
"float3":p3 = 1, 2, 3
"float4":p4 = 1, 2, 3, 4
"float12":m = [[1, 2, 3] [4, 5, 6] [7, 8, 9] [10, 11, 12]]
"inner" {
  "a":i = 1
  "b":i64 = 0x2
}
"""

text_mixed_strict = """\
bool:b=yes
str:t="hello"
int:i=0
int:i=1
long:i=2
float:r=3.0
int2:ip2=1, 2
int3:ip3=1, 2, 3
color:c=1, 2, 3, 4
float2:p2=1.0, 2.0
float3:p3=1.0, 2.0, 3.0
float4:p4=1.0, 2.0, 3.0, 4.0
float12:m=[[1.0, 2.0, 3.0] [4.0, 5.0, 6.0] [7.0, 8.0, 9.0] [10.0, 11.0, 12.0]]

inner{
  a:i=1
  b:i64=2
}\
"""


@pytest.fixture(scope='module')
def sections_only_section():
    root = Section()
    alpha = Section()
    beta = Section()
    root.add('alpha', alpha)
    root.add('beta', beta)
    return root


text_sections_only_default = """\
"alpha" {
}
"beta" {
}
"""


text_sections_only_strict = """\
alpha{
}

beta{
}\
"""


@pytest.fixture()
def ostream():
    return io.StringIO()


mixed_section_ = pytest.lazy_fixture('mixed_section')
sections_only_section_ = pytest.lazy_fixture('sections_only_section')


@pytest.mark.parametrize(['section', 'dialect', 'text'], [
    pytest.param(mixed_section_, txt.DefaultDialect, text_mixed_default, id='mixed-default'),
    pytest.param(mixed_section_, txt.StrictDialect, text_mixed_strict, id='mixed-strict'),
    pytest.param(sections_only_section_, txt.DefaultDialect, text_sections_only_default, id='sections only-default'),
    pytest.param(sections_only_section_, txt.StrictDialect, text_sections_only_strict, id='sections only-strict'),
])
def test_serialize(section, ostream, dialect, text):
    txt.serialize(section, ostream, dialect)
    ostream.seek(0)
    given = ostream.read()
    assert text == given
