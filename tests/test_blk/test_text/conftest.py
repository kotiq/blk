import textwrap
import pytest


@pytest.fixture(scope='session')
def text_mixed_default():
    """Текст секции со всеми типами значений, DefaultDialect."""

    text = """\
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
    return textwrap.dedent(text)


@pytest.fixture(scope='session')
def text_sections_only_default():
    text = """\
    "alpha" {
    }
    "beta" {
    }
    """
    return textwrap.dedent(text)


@pytest.fixture(scope='session')
def text_sections_only_strict():
    text = """\
    alpha{
    }
    
    beta{
    }"""
    return textwrap.dedent(text)


@pytest.fixture(scope='session')
def text_mixed_strict():
    """Текст секции со всеми типами значений, StrictDialect."""

    text = """\
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
    }"""
    return textwrap.dedent(text)


@pytest.fixture(scope='session')
def text_section_with_same_id_sub_default():
    """Текст секции с одинаковыми ссылками на уровне, DefaultDialect."""

    text = """\
    "sub1" {
      "scalar":i = 42
    }
    "sub2" {
      "scalar":i = 42
    }
    """
    return textwrap.dedent(text)


@pytest.fixture(scope='session')
def text_section_with_same_id_sub_deep_default():
    """Текст секции с одинаковыми ссылками с разными родителями, DefaultDialect."""

    text = """\
    "inter1" {
      "sub" {
        "scalar":i = 42
      }
    }
    "inter2" {
      "sub" {
        "scalar":i = 42
      }
    }
    """
    return textwrap.dedent(text)

