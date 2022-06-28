import pytest
from pytest import param as _
from blk.format import Format
import blk.text as txt
import blk.json as jsn
from pytest_lazyfixture import lazy_fixture
from helpers import create_text, make_outpath

outpath = make_outpath(__name__)
get = globals().__getitem__
map_names = ('single_map', 'multi_map')
for name in map_names:
    globals()[name] = lazy_fixture(name)


def serialize_text(root, ostream, out_type, is_sorted):
    if out_type is Format.STRICT_BLK:
        txt.serialize(root, ostream, dialect=txt.StrictDialect)
    elif out_type in (Format.JSON, Format.JSON_2, Format.JSON_3):
        jsn.serialize(root, ostream, out_type, is_sorted)


@pytest.mark.parametrize(['dict_section', 'dict_section_name'], [_(get(n), n, id=n) for n in map_names])
@pytest.mark.parametrize('out_type', set(Format) - {Format.RAW}, ids=lambda f: f.name.lower())
def test_out_types(dict_section, dict_section_name, out_type, outpath):
    suffix = '.txt' if out_type is Format.STRICT_BLK else '.json5'
    text_path = outpath / f'{dict_section_name}-{out_type.name.lower()}{suffix}'
    with create_text(text_path) as ostream:
        ostream.write(f'// {text_path.name}\n\n')
        serialize_text(dict_section, ostream, out_type, False)
