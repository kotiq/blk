from io import BytesIO
import pytest
from blk.types import DictSection, Name, Str
from blk.binary.bbf_constructor import InvNamesMap, NamesMap


@pytest.fixture(scope='session')
def names_bs():
    return bytes.fromhex(
        '0041 '
        '02 '
        '09 686964654E6F646573'
        '04 6E6F6465'
    )


@pytest.fixture(scope='session')
def names_map():
    nm = NamesMap([], 0x100)
    nm.update({
        0x78: Name('hideNodes'),
        0xab: Name('node'),
    })
    return nm


@pytest.fixture(scope='session')
def inv_names_map(names_map):
    inm = InvNamesMap([], names_map.module)
    inm.update({v: k for k, v in names_map.items()})
    return inm


@pytest.fixture
def names_istream(names_bs):
    return BytesIO(names_bs)


@pytest.fixture(scope='session')
def strings_bs():
    return bytes.fromhex(
        '06000040 '
        '01'
        '05 70796C6F6E'
    )


@pytest.fixture(scope='session')
def strings():
    return list(map(Str.of, (b'pylon', )))


@pytest.fixture
def strings_istream(strings_bs):
    return BytesIO(strings_bs)


@pytest.fixture(scope='session')
def data_bs():
    return bytes.fromhex(
        '0041'  # type=byte, module=0x100
        '02'  # names_count=2
        '09 686964654E6F646573'  # 'hideNodes', name_id=0x78
        '04 6E6F6465'  # 'node', name_id=0xab
        '0000'  # pad
        
        '06000040'  # type=byte, strings_data_size=6 
        '01'  # strings_count=1 
        '05 70796C6F6E'  # 'pylon', string_id=0
        '00'  # pad
        
        '0000 0100'  # params_count=0, blocks_count=1
        '780000 00'  # name_id=0x78, type_id=section_type
        '0100 0000'  # params_count=1, blocks_count=0
        'AB0000 01'  # name_id=0xab, type=str_type
        '00000000'   # string_id=0
    )


@pytest.fixture
def data_istream(data_bs):
    return BytesIO(data_bs)


@pytest.fixture(scope='session')
def dict_section():
    root = DictSection()
    sub = DictSection()
    sub.add('node', Str('pylon')),
    root.add('hideNodes', sub)
    return root


@pytest.fixture(scope='session')
def file_bs():
    return bytes.fromhex(
        # header
        '00424246'  # b'\x00BBF' magic
        '0300 0100'  # version=(3, 1)
        '34000000'  # data size=0x34
        
        # data
        # data.names
        '0041'  # type=byte, module=0x100
        '02'  # names_count=2
        '09 686964654E6F646573'  # 'hideNodes', name_id=0x78
        '04 6E6F6465'  # 'node', name_id=0xab
        '0000'  # pad
    
        # data.strings
        '06000040'  # type=byte, strings_data_size=6 
        '01'  # strings_count=1 
        '05 70796C6F6E'  # 'pylon', string_id=0
        '00'  # pad
    
        # data.block
        '0000 0100'  # params_count=0, blocks_count=1
        '780000 00'  # name_id=0x78, type_id=section_type
        '0100 0000'  # params_count=1, blocks_count=0
        'AB0000 01'  # name_id=0xab, type=str_type
        '00000000'   # string_id=0
    )


@pytest.fixture
def file_istream(file_bs):
    return BytesIO(file_bs)


@pytest.fixture(scope='session')
def compressed_file_bs():
    return bytes.fromhex(
        # header
        '0042427a'  # b'\x00BBz' magic
        '40000000'  # data size=0x40
        '3c000000'  # compressed data size=0x3c
        
        # compressed data
        '789C'
        '6370727263666064306100024726CE8CCC9454BFFC94D462963C20C9C0C0C6C0E0C0C85A5099939F0754C0C85001261918564328060070'
        'E50A30'
    )


@pytest.fixture
def compressed_file_istream(compressed_file_bs):
    return BytesIO(compressed_file_bs)
