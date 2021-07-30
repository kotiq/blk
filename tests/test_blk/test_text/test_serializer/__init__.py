from functools import partial


def dquoted(name):
    return f'"{name}"'


simple_context_base = {
    'name_text': dquoted,
    'name_type_sep': ':',
    'type_value_sep': ' = '
}


def context(base_m, m):
    m.update(base_m)
    return m


simple_context = partial(context, simple_context_base)
