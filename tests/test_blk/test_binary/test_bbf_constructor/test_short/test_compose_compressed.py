import io
from blk.types import Section
from blk.binary.bbf_constructor import compose_bbf_zlib


def test_parse(compressed_file_istream: io.BytesIO, compressed_file_bs: bytes, section: Section):
    parsed_section = compose_bbf_zlib(compressed_file_istream)
    assert compressed_file_istream.tell() == len(compressed_file_bs)
    assert parsed_section == section
