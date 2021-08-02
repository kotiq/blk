from io import BytesIO


def _test_parse_all(con, bs, validator):
    stream = BytesIO(bs)
    obj = con.parse_stream(stream)
    validator(obj)
    assert stream.tell() == len(bs)
