from test_blk.test_types.test_dict_section.test_setters.test_append import objects


def test_append_to_empty_expect_value(empty):
    section = empty
    greeting, hello = objects(2)
    section.append((greeting, hello))
    assert section == [
        (greeting, hello),
    ]


def test_append_to_empty_twice_same_name_arow_expect_multi_value(empty):
    section = empty
    greeting, hello, hola = objects(3)
    for value in (hello, hola):
        section.append((greeting, value))
    assert section == [
        (greeting, hello),
        (greeting, hola),
    ]


def test_append_to_empty_twice_same_name_alternate_expect_multi_value(empty):
    section = empty
    greeting, hello, hola, farewell, bye = objects(5)
    section.append((greeting, hello))
    section.append((farewell, bye))
    section.append((greeting, hola))
    assert section == [
        (greeting, hello),
        (farewell, bye),
        (greeting, hola),
    ]
