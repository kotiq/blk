import io
from blk.types import Section
from blk.binary.bbf_constructor import Data


def test_parse(data_istream: io.BytesIO, data_bs: bytes, section: Section):
    parsed_section = Data.parse_stream(data_istream)
    assert data_istream.tell() == len(data_bs)
    assert parsed_section == section
