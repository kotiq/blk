import logging
from pytest import raises
from blk.types import DictSection, ListSection, Long, MultiValueError, Name, Str


def get_first_name(section):
    if isinstance(section, DictSection):
        return next(iter(section.keys()))

    if isinstance(section, ListSection):
        return next(iter(section))[0]

    raise NotImplementedError


def test_add_to_empty_str_name_expect_name(empty_factory):
    section = empty_factory()
    section.add('greeting', Str('hello'))
    greeting = get_first_name(section)
    assert isinstance(greeting, Name)
    assert greeting == 'greeting'


def test_add_non_string_name_raise_type_error(empty_factory):
    section = empty_factory()
    with raises(TypeError) as ei:
        section.add(object(), Str('hello'))
    logging.info(ei.value)


def test_add_non_value_raise_type_error(empty_factory):
    section = empty_factory()
    with raises(TypeError) as ei:
        section.add(Name('greeting'), object())
    logging.info(ei.value)


def test_add_values_different_types_raise_multi_value_error(empty_factory):
    section = empty_factory()
    section.add(Name('greeting'), Str('hello'))
    with raises(MultiValueError) as ei:
        section.add(Name('greeting'), Long(0x6f6c6c6568))
    logging.info(ei)
