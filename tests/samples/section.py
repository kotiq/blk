from blk.types import Color, DictSection, Float, Float2, Float3, Float4, Float12, Int, Int2, Long, Str, true

__all__ = ['section']


def make_section():
    root = DictSection()

    gamma = DictSection()
    gamma.add('vec2i', Int2((3, 4)))
    gamma.add('vec2f', Float2((1.25, 2.5)))
    gamma.add('transform', Float12((1.0, 0.0, 0.0,
                                    0.0, 1.0, 0.0,
                                    0.0, 0.0, 1.0,
                                    1.25, 2.5, 5.0)))

    alpha = DictSection()
    alpha.add('str', Str('hello'))
    alpha.add('bool', true)
    alpha.add('color', Color((1, 2, 3, 4)))
    alpha.add('gamma', gamma)

    beta = DictSection()
    beta.add('float', Float(1.25))
    beta.add('vec2i', Int2((1, 2)))
    beta.add('vec3f', Float3((1.25, 2.5, 5.0)))

    root.add('vec4f', Float4((1.25, 2.5, 5.0, 10.0)))
    root.add('int', Int(42))
    root.add('long', Long(64))
    root.add('alpha', alpha)
    root.add('beta', beta)

    return root


section = make_section()
