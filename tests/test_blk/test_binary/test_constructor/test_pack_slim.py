import os
from blk.types import *
import blk.binary as bin
import blk.text as txt
import pytest
from helpers import outdir_rpath


@pytest.fixture(scope='module')
def outpath(buildpath):
    path = os.path.join(buildpath, outdir_rpath(__name__))
    os.makedirs(path, exist_ok=True)
    return path


@pytest.fixture(scope='module')
def section():
    root = Section()

    gamma = Section()
    gamma.add('vec2i', Int2((3, 4)))
    gamma.add('vec2f', Float2((1.25, 2.5)))
    gamma.add('transform', Float12((1.0, 0.0, 0.0,
                                    0.0, 1.0, 0.0,
                                    0.0, 0.0, 1.0,
                                    1.25, 2.5, 5.0)))

    alpha = Section()
    alpha.add('str', Str('hello'))
    alpha.add('bool', true)
    alpha.add('color', Color((1, 2, 3, 4)))
    alpha.add('gamma', gamma)

    beta = Section()
    beta.add('float', Float(1.25))
    beta.add('vec2i', Int2((1, 2)))
    beta.add('vec3f', Float3((1.25, 2.5, 5.0)))

    root.add('vec4f', Float4((1.25, 2.5, 5.0, 10.0)))
    root.add('int', Int(42))
    root.add('long', Long(64))
    root.add('alpha', alpha)
    root.add('beta', beta)

    return root


def test_pack_slim(outpath, section: Section):
    txtname = os.path.join(outpath, 'simple.txt')
    with open(txtname, 'w') as ostream:
        txt.serialize(section, ostream, dialect=txt.StrictDialect)

    names_map = {}
    bin.update_names_map(names_map, section)

    binname = os.path.join(outpath, 'simple.bin')
    with open(binname, 'wb') as ostream:
        bin.serialize_slim(section, names_map, ostream)

    namesname = os.path.join(outpath, 'simple_nm.bin')
    with open(namesname, 'wb') as ostream:
        names = names_map.keys()
        bin.serialize_names(names, ostream)

    with open(namesname, 'rb') as istream:
        names = bin.compose_names(istream)

    with open(binname, 'rb') as istream:
        root = bin.compose_slim(names, istream)

    assert root == section
