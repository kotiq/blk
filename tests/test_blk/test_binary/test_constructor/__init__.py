import io


def _test_parse_all(con, bs, validator):
    stream = io.BytesIO(bs)
    obj = con.parse_stream(stream)
    validator(obj)
    assert stream.tell() == len(bs)
