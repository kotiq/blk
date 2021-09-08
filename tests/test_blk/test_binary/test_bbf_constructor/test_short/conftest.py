import io
from collections import OrderedDict
import pytest
from blk.types import Name, Str, Section
from blk.binary.bbf_constructor import NamesMapInitContainer, ValueInfo, DataStruct


@pytest.fixture(scope='session')
def names_bs():
    return bytes.fromhex(
        '0041 '
        '02 '
        '09 686964654E6F646573'
        '04 6E6F6465'
    )


@pytest.fixture(scope='session')
def raw_names():
    return [b'hideNodes', b'node']


@pytest.fixture(scope='session')
def names_map_init(raw_names):
    return NamesMapInitContainer(raw_names, 0x100)


@pytest.fixture(scope='session')
def names_map():
    return {
        0x78: Name('hideNodes'),
        0xab: Name('node'),
    }


@pytest.fixture
def names_istream(names_bs):
    return io.BytesIO(names_bs)


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
    return io.BytesIO(strings_bs)


@pytest.fixture(scope='session')
def block_bs():
    return bytes.fromhex(
        '0000 0100'  # params_count=0, blocks_count=1
        '780000 00'  # name_id=0x78, type_id=section_type
        '0100 0000'  # params_count=1, blocks_count=0
        'AB0000 01'  # name_id=0xab, type=str_type
        '00000000'   # string_id=0
    )


@pytest.fixture(scope='session')
def values_info():
    return [
        ValueInfo(name_id=0x78, type_id=0, data=[
            ValueInfo(name_id=0xab, type_id=1, data=0)
        ])
    ]


@pytest.fixture
def block_istream(block_bs):
    return io.BytesIO(block_bs)


@pytest.fixture
def iostream():
    return io.BytesIO()


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


@pytest.fixture(scope='session')
def data():
    return DataStruct(
        names={
            0x78: Name('hideNodes'),
            0xab: Name('node')
        },
        strings=[
            Str('pylon')
        ],
        block=[
            ValueInfo(name_id=120, type_id=0, data=[
                ValueInfo(name_id=171, type_id=1, data=0)
            ])
        ]
    )


@pytest.fixture
def data_istream(data_bs):
    return io.BytesIO(data_bs)


@pytest.fixture(scope='session')
def section():
    root = Section()
    sub = Section()
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
    return io.BytesIO(file_bs)
