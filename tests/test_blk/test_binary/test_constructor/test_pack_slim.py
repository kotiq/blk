import blk.binary as bin
import blk.text as txt
from helpers import create_text, make_outpath

outpath = make_outpath(__name__)


def test_pack_slim(outpath, all_params_dict_section):
    text_path = outpath / 'simple.txt'
    with create_text(text_path) as ostream:
        txt.serialize(all_params_dict_section, ostream, dialect=txt.StrictDialect)

    inv_names = bin.InvNames.of(all_params_dict_section)

    bin_path = outpath / 'simple.bin'
    with open(bin_path, 'wb') as ostream:
        bin.serialize_slim_data(all_params_dict_section, inv_names, ostream)

    nm_path = outpath / 'simple_nm.bin'
    with open(nm_path, 'wb') as ostream:
        bin.serialize_names_data(inv_names, ostream)

    with open(nm_path, 'rb') as istream:
        names = bin.compose_names_data(istream)

    with open(bin_path, 'rb') as istream:
        root = bin.compose_partial_slim(names, istream)

    assert root == all_params_dict_section
