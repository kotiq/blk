from hashlib import sha256
from pathlib import Path
import sys

tests_dir = Path(__file__).absolute().parent.parent
sys.path.append(str(tests_dir))

from zstandard import ZstdCompressor, ZstdCompressionDict, train_dictionary
from blk import binary
from blk import text
import samples
from samples.section import section

samples_dir = Path(samples.__path__[0])

dict_digest: bytes = ...
inv_names: binary.InvNames = ...
dict_: ZstdCompressionDict = ...
no_dict_compressor: ZstdCompressor = ...
dict_compressor: ZstdCompressor = ...


def make_text():
    with open(samples_dir / 'section_txt.blk', 'w', newline='', encoding='utf8') as ostream:
        text.serialize(section, ostream)


def make_bbf():
    with open(samples_dir / 'section_bbf.blk', 'wb') as ostream:
        binary.serialize_bbf(section, ostream)


def make_fat():
    with open(samples_dir / 'section_fat.blk', 'wb') as ostream:
        binary.serialize_fat(section, ostream, strings_in_names=False)


def make_fat_s():
    with open(samples_dir / 'section_fat_s.blk', 'wb') as ostream:
        binary.serialize_fat(section, ostream, strings_in_names=True)


def make_fat_zst_set_no_dict_compressor():
    global no_dict_compressor
    no_dict_compressor = ZstdCompressor()

    with open(samples_dir / 'section_fat_zst.blk', 'wb') as ostream:
        binary.serialize_fat_zst(section, no_dict_compressor, ostream, strings_in_names=False)


def make_slim_set_nm_dict_dict_compressor():
    global inv_names
    inv_names = binary.InvNames.of(section, include_strings=True)

    with open(samples_dir / 'section_slim.blk', 'wb') as ostream:
        binary.serialize_slim(section, inv_names, ostream)

    ss = [(samples_dir / f'section_{t}.blk').read_bytes() for t in ('fat', 'slim', 'txt')]
    global dict_
    dict_ = train_dictionary(2**9, ss*10)

    global dict_compressor
    dict_compressor = ZstdCompressor(dict_data=dict_)

    global dict_digest
    dict_digest = sha256(dict_.as_bytes()).digest()

    with open((samples_dir / dict_digest.hex()).with_suffix('.dict'), 'wb') as ostream:
        ostream.write(dict_.as_bytes())

    with open(samples_dir / 'names_container', 'wb') as ostream:
        binary.serialize_partial_names(inv_names, ostream)

    with open(samples_dir / 'nm', 'wb') as ostream:
        binary.serialize_names(inv_names, dict_digest, no_dict_compressor, ostream)


def make_slim_zst():
    with open(samples_dir / f'section_slim_zst.blk', 'wb') as ostream:
        binary.serialize_slim_zst(section, inv_names, no_dict_compressor, ostream)


def make_slim_zst_dict():
    with open(samples_dir / f'section_slim_zst_dict.blk', 'wb') as ostream:
        binary.serialize_slim_zst_dict(section, inv_names, dict_compressor, ostream)


if __name__ == '__main__':
    make_text()
    make_bbf()
    make_fat()
    make_fat_s()
    make_fat_zst_set_no_dict_compressor()
    make_slim_set_nm_dict_dict_compressor()
    make_slim_zst()
    make_slim_zst_dict()
