import pytest
from pytest import param as _
from pytest_lazyfixture import lazy_fixture
from blk.binary.constructor import compose_fat, serialize_fat


@pytest.mark.parametrize(['file_istream', 'file_bs'], [
    _(*lazy_fixture(['fat_file_istream', 'fat_file_bs']), id='strings_in_strings'),
    _(*lazy_fixture(['fat_s_file_istream', 'fat_s_file_bs']), id='strings_in_names'),
])
def test_compose_fat(file_istream, file_bs, section):
    parsed_section = compose_fat(file_istream)
    assert file_istream.tell() == len(file_bs)
    assert parsed_section == section


@pytest.mark.parametrize('strings_in_names', [
    _(False, id='strings_in_strings'),
    _(True, id='strings_in_names'),
])
def test_serialize_fat(iostream, section, strings_in_names):
    serialize_fat(section, iostream, strings_in_names=strings_in_names)
    iostream.seek(0)
    assert compose_fat(iostream) == section
