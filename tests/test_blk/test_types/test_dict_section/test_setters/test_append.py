from collections import OrderedDict

def objects(x):
    return map(lambda t: object(), range(x))


def test_append_to_empty_expect_value(empty):
    section = empty
    greeting, hello = objects(2)
    section.append((greeting, hello))
    assert section == OrderedDict([
        (greeting, [hello]),
    ])


def test_append_to_empty_twice_same_name_arow_expect_multi_value(empty):
    section = empty
    greeting, hello, hola = objects(3)
    for value in (hello, hola):
        section.append((greeting, value))
    assert section == OrderedDict([
        (greeting, [hello, hola]),
    ])


def test_append_to_empty_twice_same_name_alternate_expect_multi_value(empty):
    section = empty
    greeting, hello, hola, farewell, bye = objects(5)
    section.append((greeting, hello))
    section.append((farewell, bye))
    section.append((greeting, hola))
    assert section == OrderedDict([
        (greeting, [hello, hola]),
        (farewell, [bye]),
    ])
