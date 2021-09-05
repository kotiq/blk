import os
import json
import typing as t
import blk_unpack as bbf3
import blk.json as jsn
from helpers import make_outpath, create_text

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


def test_mexico_4x4(binrespath, outpath):
    rpath = 'mexico_4x4.blk'
    ipath = os.path.join(binrespath, 'mexico-content.vromfs.bin_u', 'levels', rpath)
    with open(ipath, 'rb') as istream:
        bs = istream.read()

    bbf3_parser = bbf3.BLK(bs)
    is_sorted = False
    bbf3_parser.output_type = jsn.JSON_2
    bbf3_parser.blk_version = 3
    unpacked_data = bbf3_parser._unpack_v3()
    transform_mapping(unpacked_data)

    opath = os.path.join(outpath, f'{rpath}x')
    with create_text(opath) as ostream:
        text = json.dumps(unpacked_data, ensure_ascii=False, cls=bbf3.NoIndentEncoder, indent=2, separators=(',', ': '),
                          sort_keys=is_sorted)
        ostream.write(text)
