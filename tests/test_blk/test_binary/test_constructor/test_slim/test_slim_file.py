from blk.binary.constructor import (compose_slim, compose_slim_zst, compose_slim_zst_dict, serialize_slim,
                                    serialize_slim_zst, serialize_slim_zst_dict)


def test_compose_slim(slim_file_istream, slim_file_bs, section, names):
    parsed_section = compose_slim(names, slim_file_istream)
    assert slim_file_istream.tell() == len(slim_file_bs)
    assert parsed_section == section


def test_serialize_slim(iostream, section, names, inv_names):
    serialize_slim(section, inv_names, iostream)
    iostream.seek(0)
    assert compose_slim(names, iostream) == section


def test_compose_slim_zst(slim_zst_file_istream, slim_zst_file_bs, section, names, no_dict_decompressor):
    parsed_section = compose_slim_zst(names, slim_zst_file_istream, no_dict_decompressor)
    assert slim_zst_file_istream.tell() == len(slim_zst_file_bs)
    assert parsed_section == section


def test_serialize_slim_zst(iostream, section, names, inv_names, no_dict_compressor, no_dict_decompressor):
    serialize_slim_zst(section, inv_names, no_dict_compressor, iostream)
    iostream.seek(0)
    assert compose_slim_zst(names, iostream, no_dict_decompressor) == section


def test_compose_slim_zst_dict(slim_zst_dict_file_istream, slim_zst_dict_file_bs, section, names, dict_decompressor):
    parsed_section = compose_slim_zst_dict(names, slim_zst_dict_file_istream, dict_decompressor)
    assert slim_zst_dict_file_istream.tell() == len(slim_zst_dict_file_bs)
    assert parsed_section == section


def test_serialize_slim_zst_dict(iostream, section, names, inv_names, dict_compressor, dict_decompressor):
    serialize_slim_zst_dict(section, inv_names, dict_compressor, iostream)
    iostream.seek(0)
    assert compose_slim_zst_dict(names, iostream, dict_decompressor) == section



