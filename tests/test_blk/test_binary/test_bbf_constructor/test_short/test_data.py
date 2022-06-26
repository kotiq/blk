from blk.binary.bbf_constructor import Data


def test_parse(data_istream, data_bs, dict_section):
    parsed_section = Data.parse_stream(data_istream)
    assert data_istream.tell() == len(data_bs)
    assert parsed_section == dict_section
