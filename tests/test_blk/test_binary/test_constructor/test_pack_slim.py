from pathlib import Path
from collections import OrderedDict
from blk.types import *
import blk.binary as bin
import blk.text as txt
import pytest
from helpers import make_outpath, create_text

outpath = make_outpath(__name__)


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


def test_pack_slim(outpath: Path, section: Section):
    text_path = outpath / 'simple.txt'
    with create_text(text_path) as ostream:
        txt.serialize(section, ostream, dialect=txt.StrictDialect)

    names_map = OrderedDict()
    bin.update_names_map(names_map, section)

    bin_path = outpath / 'simple.bin'
    with open(bin_path, 'wb') as ostream:
        bin.serialize_slim(section, names_map, ostream)

    nm_path = outpath / 'simple_nm.bin'
    with open(nm_path, 'wb') as ostream:
        names = names_map.keys()
        bin.serialize_names(names, ostream)

    with open(nm_path, 'rb') as istream:
        names = bin.compose_names(istream)

    with open(bin_path, 'rb') as istream:
        root = bin.compose_slim(names, istream)

    assert root == section
