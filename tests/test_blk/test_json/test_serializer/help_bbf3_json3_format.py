import json
import typing as t
import wt_tools.blk_unpack as bbf3
from blk.format_ import Format
from helpers import create_text, make_outpath

outpath = make_outpath(__name__)


def transform_mapping(m: t.MutableMapping):
    for n, vs in m.items():
        if len(vs) > 1:
            xs = []
            for v in vs:
                if isinstance(v, t.MutableMapping):
                    transform_mapping(v)  # @r
                xs.append(v)
            m[n] = xs
        else:
            v = vs[0]
            if isinstance(v, t.MutableMapping):
                transform_mapping(v)  # @r
            m[n] = v


def test_mexico_4x4(currespath, outpath):
    rpath = 'mexico_4x4.blk'
    ipath = currespath / 'mexico-content.vromfs.bin_u' / 'levels' / rpath
    bs = ipath.read_bytes()
    bbf3_parser = bbf3.BLK(bs)
    is_sorted = False
    bbf3_parser.output_type = Format.JSON_2
    bbf3_parser.blk_version = 3
    unpacked_data = bbf3_parser._unpack_v3()
    transform_mapping(unpacked_data)

    opath = (outpath / rpath).with_suffix('.json')
    with create_text(opath) as ostream:
        text = json.dumps(unpacked_data, ensure_ascii=False, cls=bbf3.NoIndentEncoder, indent=2, separators=(',', ': '),
                          sort_keys=is_sorted)
        ostream.write(text)
