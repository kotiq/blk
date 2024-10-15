from blk.types import (Bool, Color, DictSection, Float, Float2, Float3, Float4, Float12, Int, Int2, Int3, Long,
                       ListSection, Name, Str, Scalar, Vector)
from pytest import mark, param as _


def get_first_item(section):
    if isinstance(section, DictSection):
        name, (value, ) = next(iter(section.items()))
        return name, value

    if isinstance(section, ListSection):
        return next(iter(section))

    raise NotImplementedError


@mark.parametrize(['type_', 'args'], [
    _(Str, ('hello', ), id='Str'),
    _(Int, (42, ), id='Int'),
    _(Float, (1.0, ), id='Float'),
    _(Float2, (1.0, 2.0), id='Float2'),
    _(Float3, (1.0, 2.0, 3.0), id='Float3'),
    _(Float4, (1.0, 2.0, 3.0, 4.0), id='Float4'),
    _(Int2, (1, 2), id='Int2'),
    _(Int3, (1, 2, 3), id='Int3'),
    _(Color, (1, 2, 3, 4), id='Color'),
    _(Float12, (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12), id='Float12'),
    _(Long, (1, ), id='Long'),
])
def test_add_type_str_name_type_value_expect_item(empty_factory, type_, args: tuple):
    section = empty_factory()
    name_ = type_.__name__.lower()
    setter_name = f'add_{name_}'
    setter = getattr(section, setter_name)
    setter(name_, *args)
    name, value = get_first_item(section)

    assert isinstance(name, Name)
    assert name == name_

    assert isinstance(value, type_)
    if isinstance(value, Scalar):
        assert value == args[0]
    elif isinstance(value, Vector):
        assert value == args
    else:
        raise NotImplementedError


@mark.parametrize('value_', [False, True])
def test_add_bool_str_name_expect_item(empty_factory, value_):
    section = empty_factory()
    name_ = str(value_).lower()
    setter_name = f'add_{name_}'
    setter = getattr(section, setter_name)
    setter(name_)
    name, value = get_first_item(section)

    assert isinstance(name, Name)
    assert name == name_

    assert isinstance(value, Bool)
    assert value == value_


def test_add_color_str_name_triple_expect_item_default_alpha(empty_factory):
    section = empty_factory()
    name_ = 'color'
    args = (1, 2, 3)
    section.add_color(name_, *args)
    name, value = get_first_item(section)

    assert isinstance(name, Name)
    assert name == name_

    assert isinstance(value, Color)
    assert value == (*args, 255)
