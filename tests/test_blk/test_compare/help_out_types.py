from pathlib import Path
import typing as t
import pytest
from blk.types import *
import blk.text as txt
import blk.json as jsn
from pytest_lazyfixture import lazy_fixture
from helpers import create_text, make_outpath

outpath = make_outpath(__name__)


@pytest.fixture(scope='module')
def single_map():
    root = Section()
    root.add('a', Int(1))
    root.add('b', Int(2))
    root.add('c', Int(3))
    sub = Section()
    sub.add('x', Float(4))
    sub.add('y', Float(5))
    root.add('sub', sub)
    return root


@pytest.fixture(scope='module')
def multi_map():
    root = Section()
    root.add('a', Int(1))
    root.add('a', Int(2))
    root.add('b', Int(3))
    sub = Section()
    sub.add('x', Float(4))
    sub.add('y', Float(5))
    root.add('sub', sub)
    return root


out_type_map = {
    'strict_blk': txt.STRICT_BLK,
    'json': jsn.JSON,
    'json_2': jsn.JSON_2,
    'json_3': jsn.JSON_3,
}


def serialize_text(root: Section, ostream: t.TextIO, out_type: int, is_sorted: bool):
    if out_type == txt.STRICT_BLK:
        txt.serialize(root, ostream, dialect=txt.StrictDialect)
    elif out_type in (jsn.JSON, jsn.JSON_2, jsn.JSON_3):
        jsn.serialize(root, ostream, out_type, is_sorted)


@pytest.mark.parametrize(['section', 'section_name'], [
    pytest.param(lazy_fixture('single_map'), 'single_map', id='single_map'),
    pytest.param(lazy_fixture('multi_map'), 'multi_map', id='multi_map'),
])
@pytest.mark.parametrize('out_type_name', out_type_map.keys())
def test_out_types(dict_section, section_name, out_type_name: str, outpath: Path):
    out_type = out_type_map[out_type_name]
    suffix = '.txt' if out_type_name == 'strict_blk' else '.json'
    text_path = outpath / f'{section_name}-{out_type_name}{suffix}'
    with create_text(text_path) as ostream:
        ostream.write(f'// {text_path.name}\n\n')
        serialize_text(dict_section, ostream, out_type, False)
