from collections import OrderedDict
from blk.types import Name, Str


def test_add_to_empty_expect_value(empty):
    section = empty
    greeting = Name('greeting')
    hello = Str('Hello')
    section.add(greeting, hello)
    assert section == OrderedDict([
        (greeting, [hello]),
    ])


def test_add_to_empty_twice_same_name_arow_expect_multi_value(empty):
    section = empty
    greeting = Name('greeting')
    hello, hola = map(Str, ('hello', 'hola'))
    for value in (hello, hola):
        section.add(greeting, value)
    assert section == OrderedDict([
        (greeting, [hello, hola]),
    ])


def test_add_to_empty_twice_same_name_alternate_expect_multi_value(empty):
    section = empty
    greeting, farewell = map(Name, ('greeting', 'farewell'))
    hello, hola, bye = map(Str, ('hello', 'hola', 'bye'))
    section.add(greeting, hello)
    section.add(farewell, bye)
    section.add(greeting, hola)
    assert section == OrderedDict([
        (greeting, [hello, hola]),
        (farewell, [bye]),
    ])
