from blk.binary.constructor import compose_names, serialize_names


def test_compose_names(names_file_istream, names_file, no_dict_decompressor, names_file_bs):
    parsed_names_file = compose_names(names_file_istream, no_dict_decompressor)
    assert names_file_istream.tell() == len(names_file_bs)
    assert parsed_names_file == names_file


def test_serialize_names(iostream, names_file, inv_names, dict_digest, no_dict_decompressor, no_dict_compressor):
    serialize_names(inv_names, dict_digest, no_dict_compressor, iostream)
    iostream.seek(0)
    assert compose_names(iostream, no_dict_decompressor) == names_file
