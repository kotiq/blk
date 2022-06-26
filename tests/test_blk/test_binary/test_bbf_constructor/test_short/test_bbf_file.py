from blk.binary.bbf_constructor import BBFFile


def test_parse(file_istream, file_bs, dict_section):
    parsed_section = BBFFile.parse_stream(file_istream)
    assert file_istream.tell() == len(file_bs)
    assert parsed_section == dict_section
