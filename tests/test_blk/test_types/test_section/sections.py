from blk import Name, Section, Float2, Float3, Str


flat_section = Section([
    (Name('a'), [Float2((1, 2)), Float2((3, 4))]),
    (Name('b'), [Float3((5, 6, 7))]),
    (Name('c'), [Str('hello')]),
])


nested_section = Section([
    (Name('a'), [Str('hello')]),
    (Name('b'), [Section([(Name('c'), [Str('nested')])])]),
    (Name('d'), [Str('world')])
])
