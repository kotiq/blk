import io
import os
import sys
import itertools as itt
import typing as t
import construct as ct
import pytest
from blk.types import *
from blk.binary.constants import types_codes_map
from blk.binary.bbf_constructor import (create_inv_names_map, create_inv_strings, true_id, false_id, types_cons_map,
                                        Offset, BBFFile)
from helpers import make_outpath

outpath = make_outpath(__name__)


def byte_str(b: int) -> str:
    return format(b, '02x')


def dump_map(m: t.Mapping[t.Any, int], file: t.TextIO):
    print('{', file=file)
    for v, h in m.items():
        print(f'    {v!r}: {h:#04x}', file=file)
    print('}', file=file)


def dump_pascalstrings(it: t.Iterable[bytes], file: t.TextIO):
    for e in it:
        sz = len(e)
        print(f'{sz:#04x}', end='', file=file)
        if sz:
            print(f' {e}', file=file)


def encode_str(s: str) -> bytes:
    return s.encode()


@pytest.fixture(scope='module')
def inv_names_map(section: Section):
    return create_inv_names_map(section.names(), 0x100)


def test_create_names(inv_names_map: t.Mapping[Name, int]):
    print()
    print('inv_names_map')
    dump_map(inv_names_map, sys.stdout)
    print()
    names_count = len(inv_names_map)
    print(f'len(inv_names_map) = {names_count:#04x}')
    print()
    print('pascal strings')
    it = map(encode_str, inv_names_map)
    it1, it2 = itt.tee(it, 2)
    dump_pascalstrings(it1, sys.stdout)
    print()
    print('names block:')
    print("'0041'")
    print(repr(byte_str(names_count)))
    for bs in it2:
        print(repr(byte_str(len(bs)) + ' ' + bs.hex()))


@pytest.fixture(scope='module')
def inv_strings(section: Section):
    return create_inv_strings(section.strings())


def test_create_strings(inv_strings: t.Mapping[Str, int]):
    print()
    print('inv_strings:')
    dump_map(inv_strings, sys.stdout)
    print()
    strings_count = len(inv_strings)
    print(f'len(inv_strings) = {strings_count:#04x}')
    print()
    print('pascal strings')
    it = map(encode_str, inv_strings)
    it1, it2, it3 = itt.tee(it, 3)
    dump_pascalstrings(it1, sys.stdout)
    print()
    print('strings block:')

    if not strings_count:
        print('00000000')
    else:
        strings_block_size = 1 + sum(map(lambda bs: 1 + len(bs), it2))
        print(repr(strings_block_size.to_bytes(2, 'little').hex() + '0040'))
        print(repr(byte_str(strings_count)))
        for bs in it3:
            print(repr(byte_str(len(bs)) + ' ' + bs.hex()))


def dump_section(section: Section, inv_names_map: t.Mapping[Name, int], inv_strings: t.Mapping[Str, int],
                 file: t.TextIO):
    param_pairs, blocks_pairs = section.split_values()
    params_count = len(param_pairs)
    blocks_count = len(blocks_pairs)
    print(repr(params_count.to_bytes(2, 'little').hex() + ' ' + blocks_count.to_bytes(2, 'little').hex()), file=file)

    for name, param in param_pairs:
        if param is true:
            type_id = true_id
        elif param is false:
            type_id = false_id
        else:
            cls = param.__class__
            type_id = types_codes_map[cls]
        name_id = inv_names_map[name]
        print(repr(ct.Int24ul.build(name_id).hex() + ' ' + byte_str(type_id)), file=file)

    for name, param in param_pairs:
        cls = param.__class__
        if cls is not Bool:
            if cls is Str:
                con = Offset
                value = inv_strings[param]
            else:
                con = types_cons_map[cls]
                value = param
            bs = con.build(value)
            print(repr(bs.hex()), file=file)

    for name, block in blocks_pairs:
        name_id = inv_names_map[name]
        type_id = types_codes_map[Section]
        print(repr(ct.Int24ul.build(name_id).hex() + ' ' + byte_str(type_id)), file=file)
        dump_section(block, inv_names_map, inv_strings, file=file)


def test_create_block(section: Section, inv_names_map: t.Mapping[Name, int], inv_strings: t.Mapping[Str, int]):
    print('section block:')
    dump_section(section, inv_names_map, inv_strings, sys.stdout)


@pytest.fixture(scope='module')
def file_path(outpath):
    return os.path.join(outpath, 'all_types.blk')


def test_dump(file_bs: bytes, file_path: str):
    with open(file_path, 'wb') as ostream:
        ostream.write(file_bs)


def test_parse(file_istream: io.BytesIO, file_bs: bytes, section: Section):
    parsed_section = BBFFile.parse_stream(file_istream)
    assert file_istream.tell() == len(file_bs)
    assert parsed_section == section
