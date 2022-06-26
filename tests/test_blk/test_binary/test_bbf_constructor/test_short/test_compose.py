from blk.binary.bbf_constructor import compose_bbf


def test_parse(file_istream, file_bs, dict_section):
    parsed_section = compose_bbf(file_istream)
    assert file_istream.tell() == len(file_bs)
    assert parsed_section == dict_section
