import io
import pytest
from blk.types import *


@pytest.fixture(scope='session')
def section():
    root = Section()
    root.add('str', Str('hello'))
    root.add('int', Int(1))
    root.add('float', Float(1.0))
    root.add('float2', Float2((1.0, 2.0)))
    root.add('float3', Float3((1.0, 2.0, 3.0)))
    root.add('float4', Float4((1.0, 2.0, 3.0, 4.0)))
    root.add('int2', Int2((1, 2)))
    root.add('int3', Int3((1, 2, 3)))
    root.add('bool', true)
    root.add('color', Color((1, 2, 3, 4)))
    root.add('float12', Float12((1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0)))
    root.add('long', Long(1))

    section_11 = Section()
    section_11.add('str', Str('world'))
    section_11.add('int', Int(2))
    section_21 = Section()
    section_21.add('float', Float(2.0))
    section_21.add('bool', false)
    section_11.add('section_21', section_21)
    root.add('section_11', section_11)

    section_12 = Section()
    section_12.add('int', Int(3))
    section_12.add('int', Int(4))
    section_12.add('int', Int(5))
    section_12.add('int', Int(6))
    section_12.add('int', Int(7))
    root.add('section_12', section_12)

    return root


@pytest.fixture(scope='session')
def file_bs():
    return bytes.fromhex(
        '00424246'
        '0300 0100'
        '90010000'

        '0041'
        '0f'
        '03 737472'
        '03 696e74'
        '05 666c6f6174'
        '06 666c6f617432'
        '06 666c6f617433'
        '06 666c6f617434'
        '04 696e7432'
        '04 696e7433'
        '04 626f6f6c'
        '05 636f6c6f72'
        '07 666c6f61743132'
        '04 6c6f6e67'
        '0a 73656374696f6e5f3131'
        '0a 73656374696f6e5f3231'
        '0a 73656374696f6e5f3132'
        '000000'

        '0d000040'
        '02'
        '05 68656c6c6f'
        '05 776f726c64'
        '000000'

        '0c00 0200'
        '7e0000 01'
        '300000 02'
        '9b0000 03'
        '2d0000 04'
        '2e0000 05'
        '2f0000 06'
        '620000 07'
        '630000 08'
        '910000 09'
        '440000 0a'
        'de0000 0b'
        '350000 0c'
        '00000000'
        '01000000'
        '0000803f'
        '0000803f00000040'
        '0000803f0000004000004040'
        '0000803f000000400000404000008040'
        '0100000002000000'
        '010000000200000003000000'
        '01020304'
        '0000803f0000004000004040000080400000a0400000c0400000e0400000004100001041000020410000304100004041'
        '0100000000000000'
        '3b0000 00'
        '0200 0100'
        '7e0000 01'
        '300000 02'
        '01000000'
        '02000000'
        '5c0000 00'
        '0200 0000'
        '9b0000 03'
        '910000 89'
        '00000040'
        '3c0000 00'
        '0500 0000'
        '300000 02'
        '300000 02'
        '300000 02'
        '300000 02'
        '300000 02'
        '03000000'
        '04000000'
        '05000000'
        '06000000'
        '07000000'
    )


@pytest.fixture
def file_istream(file_bs):
    return io.BytesIO(file_bs)
