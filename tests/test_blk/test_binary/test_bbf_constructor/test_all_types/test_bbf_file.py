from blk.binary.bbf_constructor import BBFFile


def test_parse(file_istream, file_bs, dict_section):
    parsed_section = BBFFile.parse_stream(file_istream)
    assert file_istream.tell() == len(file_bs)
    assert parsed_section == dict_section


def test_build(iostream, file_bs, dict_section):
    BBFFile.build_stream(dict_section, iostream, version=(3, 1), module=0x100)
    assert iostream.tell() == len(file_bs)
    iostream.seek(0)
    built_section = BBFFile.parse_stream(iostream)
    assert built_section == dict_section
