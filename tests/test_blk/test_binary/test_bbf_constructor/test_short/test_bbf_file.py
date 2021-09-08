import io
from blk.types import Section
from blk.binary.bbf_constructor import BBFFile


def test_parse(file_istream: io.BytesIO, file_bs: bytes, section: Section):
    parsed_section = BBFFile.parse_stream(file_istream)
    assert file_istream.tell() == len(file_bs)
    assert parsed_section == section
