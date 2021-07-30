import os
from enum import Enum
from io import BytesIO
import construct as ct
from construct import this
import zstandard


def not_implemented(obj, ctx):
    raise NotImplementedError


class HeaderType(Enum):
    SIMPLE = b's'
    EXTENDED = b'x'


class Platform(Enum):
    PC = b'\x00\x00PC'
    IOS = b'\x00iOS'
    ANDROID = b'\x00and'


class VromfsType(Enum):
    MAYBE_ZLIB = 0x80
    ZSTD = 0xc0


class PackType(Enum):
    NONE = 'none'
    ZLIB = 'zlib'
    ZSTD = 'zstd'


def getvalue(val, context):
    return val(context) if callable(val) else val


def pack_type(code, size):
    code = VromfsType[code]

    if code is VromfsType.MAYBE_ZLIB:
        if not size:
            return PackType.NONE
        return PackType.ZLIB
    if code is VromfsType.ZSTD:
        return PackType.ZSTD
    raise ValueError('Неизвестный код упаковки: {}'.format(code))


Version = ct.ExprAdapter(ct.Bytes(4), lambda o, c: tuple(reversed(o)), not_implemented)

Header = ct.Struct(
    'magic' / ct.Const(b'VRF'),
    'type' / ct.Enum(ct.Bytes(1), HeaderType),
    'platform' / ct.Enum(ct.Bytes(4), Platform),
    'original_size' / ct.Int32ul,
    'packed_size' / ct.Int24ul,
    'vromfs_type' / ct.Enum(ct.Byte, VromfsType),
    'vromfs_packed_type' / ct.Computed(lambda c: pack_type(c.vromfs_type, c.packed_size)),
    'ext_header' / ct.If(
        lambda c: HeaderType[c.type] is HeaderType.EXTENDED,
        ct.Struct(
            'size' / ct.Int16ul,
            'flags' / ct.Int16ul,
            'version' / Version
        )
    ),
)


def xor(xs, ys):
    return bytes(x ^ y for x, y in zip(xs, ys))


class DeobfsAdapter(ct.Adapter):
    def __init__(self, subcon, ns=None):
        super().__init__(subcon)
        self.ns = ns

    def _decode(self, obj: bytes, context, path) -> bytes:
        packed_size = context.header.packed_size
        is16lt = packed_size >= 16
        is32lt = packed_size >= 32
        pad = packed_size % 4
        skip = (32 if is32lt else 16 if is16lt else 0) + pad
        need_read_size = packed_size - skip
        stream = BytesIO(obj)

        first_part = xor(ct.Bytes(16).parse_stream(stream), bytes.fromhex('55aa55aa 0ff00ff0 55aa55aa 48124812')) \
            if is16lt else b''
        middle = ct.Bytes(need_read_size).parse_stream(stream)
        second_part = xor(ct.Bytes(16).parse_stream(stream), bytes.fromhex('48124812 55aa55aa 0ff00ff0 55aa55aa')) \
            if is32lt else b''
        align_tail = ct.Bytes(pad).parse_stream(stream) if pad else b''

        deobfs_compressed_data = first_part + middle + second_part + align_tail
        if self.ns is not None:
            self.ns.deobfs_compressed_data = deobfs_compressed_data
        return deobfs_compressed_data


class ZstdStreamAdapter(ct.Adapter):
    def __init__(self, subcon, max_output_size, ns=None):
        super().__init__(subcon)
        self.max_output_size = max_output_size
        self.ns = ns

    def _decode(self, obj: bytes, context, path) -> bytes:
        max_output_size = getvalue(self.max_output_size, context)
        dctx = zstandard.ZstdDecompressor()
        decompressed_data = dctx.decompress(obj, max_output_size)
        if self.ns is not None:
            self.ns.decompressed_data = decompressed_data
        return decompressed_data


class NotPackedStreamAdapter(ct.Adapter):
    def _decode(self, obj: bytes, context, path) -> ct.Container:
        stream = BytesIO(obj)
        return ct.Struct(
            'data_start_offset' / ct.Tell,
            'filename_table_offset' / ct.Int32ul,
            'files_count' / ct.Int32ul,
            ct.Seek(8, os.SEEK_CUR),
            'filedata_table_offset' / ct.Int32ul,
        ).parse_stream(stream)


def parse_file(path, ns=None):
    return ct.Struct(
        'header' / Header,
        'body' / ct.Switch(
            this.header.vromfs_packed_type, {
                PackType.ZSTD: NotPackedStreamAdapter(ZstdStreamAdapter(
                    DeobfsAdapter(ct.Bytes(this.header.packed_size), ns),
                    this.header.original_size,
                    ns
                )),
            }
        ),
        'tail' / ct.GreedyBytes,
    ).parse_file(path)
