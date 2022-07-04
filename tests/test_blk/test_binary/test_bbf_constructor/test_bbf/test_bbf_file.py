from blk.binary.bbf_constructor import compose_bbf, serialize_bbf


def test_compose_bbf(bbf_file_istream, bbf_file_bs, section):
    parsed_section = compose_bbf(bbf_file_istream)
    assert bbf_file_istream.tell() == len(bbf_file_bs)
    assert parsed_section == section


def test_serialize_bbf(iostream, section):
    serialize_bbf(section, iostream)
    iostream.seek(0)
    assert compose_bbf(iostream) == section
