import io
from blk.types import *
from blk.binary.bbf_constructor import BBFFile


def test_parse(file_istream: io.BytesIO, file_bs: bytes, section: Section):
    parsed_section = BBFFile.parse_stream(file_istream)
    assert file_istream.tell() == len(file_bs)
    assert parsed_section == section


def test_build(iostream: io.BytesIO, file_bs: bytes, section: Section):
    BBFFile.build_stream(section, iostream, version=(3, 1), module=0x100)
    assert iostream.tell() == len(file_bs)
    iostream.seek(0)
    built_section = BBFFile.parse_stream(iostream)
    assert built_section == section
