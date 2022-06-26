from io import BytesIO
import pytest
from blk.types import Color, DictSection, Float, Float2, Float3, Float4, Float12, Int, Int2, Long, Name, Str, true
from blk.binary.constructor import InvNames


@pytest.fixture(scope='module')
def dict_sections_only_dict_section():
    a = DictSection()
    b = DictSection()
    c = DictSection()
    d = DictSection()
    e = DictSection()
    f = DictSection()
    g = DictSection()
    h = DictSection()
    i = DictSection()
    j = DictSection()
    k = DictSection()
    l = DictSection()

    a.append(Name('b'), b)
    a.append(Name('c'), c)
    a.append(Name('d'), d)
    a.append(Name('e'), e)

    c.append(Name('f'), f)
    c.append(Name('g'), g)

    e.append(Name('h'), h)
    e.append(Name('i'), i)
    e.append(Name('j'), j)

    g.append(Name('k'), k)
    g.append(Name('l'), l)

    return a


@pytest.fixture(scope='module')
def all_params_dict_section():
    root = DictSection()

    gamma = DictSection()
    gamma.add('vec2i', Int2((3, 4)))
    gamma.add('vec2f', Float2((1.25, 2.5)))
    gamma.add('transform', Float12((1.0, 0.0, 0.0,
                                    0.0, 1.0, 0.0,
                                    0.0, 0.0, 1.0,
                                    1.25, 2.5, 5.0)))

    alpha = DictSection()
    alpha.add('str', Str('hello'))
    alpha.add('bool', true)
    alpha.add('color', Color((1, 2, 3, 4)))
    alpha.add('gamma', gamma)

    beta = DictSection()
    beta.add('float', Float(1.25))
    beta.add('vec2i', Int2((1, 2)))
    beta.add('vec3f', Float3((1.25, 2.5, 5.0)))

    root.add('vec4f', Float4((1.25, 2.5, 5.0, 10.0)))
    root.add('int', Int(42))
    root.add('long', Long(64))
    root.add('alpha', alpha)
    root.add('beta', beta)

    return root


@pytest.fixture(scope='module')
def dict_sections_only_dict_section_fat_data_bs():
    return bytes.fromhex(
        '0b'  # names_count
        '16'  # names_bytes_count
        '6200 6300 6600 6700 6b00 6c00 6400 6500 6800 6900 6a00'  # names_bytes
        '0c'  # blocks_count
        '00'  # params_count
        '00'  # params_data
        '00 00 04 01'  # blocks_count
        '01 00 00'
        '02 00 02 05'
        '07 00 00'
        '08 00 03 07'
        '03 00 00'
        '04 00 02 0a'
        '09 00 00'
        '0a 00 00'
        '0b 00 00'
        '05 00 00'
        '06 00 00'
    )


@pytest.fixture(scope='module')
def all_params_dict_section_fat_data_bs():
    return bytes.fromhex(
        # names
        '0e'  # names_count
        '51'  # names_bytes_count
        # names_data
        '766563346600'  # 0 'vec4f'
        '696e7400'  # 1 'int'
        '6c6f6e6700'  # 2 'long'
        '616c70686100'  # 3 'alpha'
        '73747200'  # 4 'str'
        '626f6f6c00'  # 5 'bool'
        '636f6c6f7200'  # 6 'color'
        '67616d6d6100'  # 7 'gamma'
        '766563326900'  # 8 'vec2i'
        '766563326600'  # 9 'vec2f'
        '7472616e73666f726d00'  # 0xa 'transform'
        '6265746100'  # 0xb 'beta'
        '666c6f617400'  # 0xc 'float'
        '766563336600'  # 0xd 'vec3f'
        # block
        '04'  # blocks_count
        '0c'  # params_count
        # params_data
        '74'  # params_data_bytes_count
        # params_data_bytes
        #0 1 2 3  4 5 6 7  8 9 a b  c d e f 
        '68656c6c 6f000000 0000a03f 00002040'  # 00 (0x00, 'hello'), pad=2*b'\x00', (0x08, (1.25f, 2.5f, 5.0f, 10.0f))
        '0000a040 00002041 40000000 00000000'  # 10 (0x18, 64L)
        '01000000 02000000 0000a03f 00002040'  # 20 (0x20, (1, 2)), (0x28, (1.25f, 2.5f, 5.0f))
        '0000a040 03000000 04000000 0000a03f'  # 30 (0x34, (3, 4)), (0x3c, (1.25f, 2.5f))
        '00002040 0000803f 00000000 00000000'  # 40 (0x44, ((1.0f, 0.0f, 0.0f), (0.0f, 1.0f, 0.0f), (0.0f, 0.0f, 1.0f),
        '00000000 0000803f 00000000 00000000'  # 50 (1.25f, 2.5f, 5.0f)))
        '00000000 0000803f 0000a03f 00002040'  # 60
        '0000a040'                             # 70
        # params
        '000000 06 08000000'  # 0 ('vec4f', Float4, @0x08~(1.25f, 2.5f, 5.0f, 10.0f))
        '010000 02 2a000000'  # 1 ('int', Int, 42)
        '020000 0c 18000000'  # 2 ('long', Long, @0x18~64L)
        '040000 01 00000000'  # 3 ('str', Str, 'hello')
        '050000 09 01000000'  # 4 ('bool', Bool, True)
        '060000 0a 03020104'  # 5 ('color', Color, #01020304)
        '0c0000 03 0000a03f'  # 6 ('float', Float, 1.25f)
        '080000 07 20000000'  # 7 ('vec2i', Int2, @0x20~(1, 2))
        '0d0000 05 28000000'  # 8 ('vec3f', Float3, @0x28~(1.25f, 2.5f, 5.0f))
        '080000 07 34000000'  # 9 ('vec2i', Int2, @0x34~(3, 4))
        '090000 04 3c000000'  # 0xa ('vec2f', Float2, @0x3c~(1.25f, 2.5f))
        '0a0000 0b 44000000'  # 0xb ('transform', Float12, @0x044~(A=E_f, T=(1.25f, 2.5f, 5.0f)))
        # blocks
        '00 03 02 01'  # root, 3 params, 2 blocks, started at 1 ('alpha', 'beta')
        '04 03 01 03'  # 0x3~'alpha', 3 params, 1 blocks, stared at 3 ('gamma')
        '0c 03 00'     # 0xb~'beta', 3 params, 0 blocks
        '08 03 00'     # 0x7~'gamma', 3 params, 0 blocks
)


@pytest.fixture(scope='module')
def all_params_dict_section_fat_s_data_bs():
    return bytes.fromhex(
        # names
        '0f'
        '57'
        
        '766563346600'  # 0
        '696e7400'  # 1
        '6c6f6e6700'  # 2
        '616c70686100'  # 3
        '73747200'  # 4
        '626f6f6c00'  # 5
        '636f6c6f7200'  # 6
        '67616d6d6100'  # 7
        '766563326900'  # 8
        '766563326600'  # 9
        '7472616e73666f726d00'  # 0xa
        '6265746100'  # 0xb
        '666c6f617400'  # 0xc
        '766563336600'  # 0xd
        '68656c6c6f00'  # 0xe 'hello'
        # block
        '04'
        '0c'
        # params_data
        '6c'        
        '0000a03f 00002040 0000a040 00002041'  # 00
        '40000000 00000000 01000000 02000000'  # 10
        '0000a03f 00002040 0000a040 03000000'  # 20
        '04000000 0000a03f 00002040 0000803f'  # 30
        '00000000 00000000 00000000 0000803f'  # 40
        '00000000 00000000 00000000 0000803f'  # 50
        '0000a03f 00002040 0000a040'           # 60
        # params
        '000000 06 00000000'
        '010000 02 2a000000'
        '020000 0c 10000000'
        '040000 01 0e000080'  # 4  ('str', Str, #0xe~'hello')
        '050000 09 01000000'
        '060000 0a 03020104'
        '0c0000 03 0000a03f'
        '080000 07 18000000'
        '0d0000 05 20000000'
        '080000 07 2c000000'
        '090000 04 34000000'
        '0a0000 0b 3c000000'
        # blocks        
        '00 03 02 01'
        '04 03 01 03'
        '0c 03 00'
        '08 03 00'
    )


@pytest.fixture(scope='module')
def all_params_dict_section_slim_data_bs():
    return bytes.fromhex(
        # external names
        '00'
        # block
        '04'
        '0C'
        # params_data
        '6C'
        '0000A03F 00002040 0000A040 00002041'  # 00
        '40000000 00000000 01000000 02000000'  # 10
        '0000A03F 00002040 0000A040 03000000'  # 20
        '04000000 0000A03F 00002040 0000803F'  # 30
        '00000000 00000000 00000000 0000803F'  # 40
        '00000000 00000000 00000000 0000803F'  # 50
        '0000A03F 00002040 0000A040'           # 60
        # params
        '000000 06 00000000'
        '010000 02 2A000000'
        '020000 0C 10000000'
        '040000 01 0E000080'
        '050000 09 01000000'
        '060000 0A 03020104'
        '0C0000 03 0000A03F'
        '080000 07 18000000'
        '0D0000 05 20000000'
        '080000 07 2C000000'
        '090000 04 34000000'
        '0A0000 0B 3C000000'
        # blocks
        '00 03 02 01'
        '04 03 01 03'
        '0C 03 00'
        '08 03 00'
    )


@pytest.fixture(scope='module')
def all_params_dict_section_fat_bs(all_params_dict_section_fat_data_bs):
    return b'\x01' + all_params_dict_section_fat_data_bs


@pytest.fixture(scope='module')
def all_params_dict_section_fat_s_bs(all_params_dict_section_fat_s_data_bs):
    return b'\x01' + all_params_dict_section_fat_s_data_bs


@pytest.fixture(scope='module')
def all_params_dict_section_names_seq():
    return [Name(t) for t in (
        'vec4f', 'int', 'long', 'alpha', 'str', 'bool', 'color', 'gamma', 'vec2i', 'vec2f', 'transform', 'beta',
        'float', 'vec3f', 'hello'
    )]


@pytest.fixture(scope='module')
def all_params_dict_section_inv_names(all_params_dict_section_names_seq):
    return InvNames(all_params_dict_section_names_seq)


@pytest.fixture
def empty_inv_names():
    return InvNames()


@pytest.fixture(scope='module')
def all_params_dict_section_slim_bs(all_params_dict_section_slim_data_bs):
    return b'\x03' + all_params_dict_section_slim_data_bs


@pytest.fixture
def dict_sections_only_dict_section_fat_data_istream(dict_sections_only_dict_section_fat_data_bs):
    return BytesIO(dict_sections_only_dict_section_fat_data_bs)


@pytest.fixture
def all_params_dict_section_fat_data_istream(all_params_dict_section_fat_data_bs):
    return BytesIO(all_params_dict_section_fat_data_bs)


@pytest.fixture
def all_params_dict_section_fat_s_data_istream(all_params_dict_section_fat_s_data_bs):
    return BytesIO(all_params_dict_section_fat_s_data_bs)


@pytest.fixture
def all_params_dict_section_fat_istream(all_params_dict_section_fat_bs):
    return BytesIO(all_params_dict_section_fat_bs)


@pytest.fixture
def all_params_dict_section_fat_s_istream(all_params_dict_section_fat_s_bs):
    return BytesIO(all_params_dict_section_fat_s_bs)


@pytest.fixture
def all_params_dict_section_slim_data_istream(all_params_dict_section_slim_data_bs):
    return BytesIO(all_params_dict_section_slim_data_bs)


@pytest.fixture
def all_params_dict_section_slim_istream(all_params_dict_section_slim_bs):
    return BytesIO(all_params_dict_section_slim_bs)


@pytest.fixture
def ostream():
    return BytesIO()


@pytest.fixture()
def iostream():
    return BytesIO()

