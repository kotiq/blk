import io
from blk.types import Section
from blk.binary.bbf_constructor import DataStructCon, DataStruct, DataAdapter


def test_parse(data_istream: io.BytesIO, data_bs: bytes, data: DataStruct):
    parsed_data: DataStruct = DataStructCon.parse_stream(data_istream)
    assert data_istream.tell() == len(data_bs)
    assert parsed_data == data


def test_decode(data: DataStruct, section: Section):
    decoded_section = DataAdapter._decode(None, data, None, None)
    assert decoded_section == section
