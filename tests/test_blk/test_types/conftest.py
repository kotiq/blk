from pytest import fixture, param as _
from blk.types import (Float, Float2, Int, Int2, Long, SafeFloat, SafeFloat2, SafeInt, SafeInt2, SafeLong, SafeStr,
                       SafeUByte, Str, UByte, )


@fixture(scope='module', params=[
    _(Str.of, id='Str.of'),
    _(SafeStr, id='SafeStr'),
])
def safe_str_factory(request):
    return request.param


@fixture(scope='module', params=[
    _(Int.of, id='Int.of'),
    _(SafeInt, id='SafeInt'),
])
def safe_int_factory(request):
    return request.param


@fixture(scope='module', params=[
    _(UByte.of, id='UByte.of'),
    _(SafeUByte, id='SafeUByte'),
])
def safe_ubyte_factory(request):
    return request.param


@fixture(scope='module', params=[
    _(Long.of, id='Long.of'),
    _(SafeLong, id='SafeLong'),
])
def safe_long_factory(request):
    return request.param


@fixture(scope='module', params=[
    _(Float.of, id='Float.of'),
    _(SafeFloat, id='SafeFloat'),
])
def safe_float_factory(request):
    return request.param


@fixture(scope='module', params=[
    _(Int2.of, id='Int2.of'),
    _(SafeInt2, id='SafeInt2'),
])
def safe_int2_factory(request):
    return request.param


@fixture(scope='module', params=[
    _(Float2.of, id='Float2.of'),
    _(SafeFloat2, id='SafeFloat2'),
])
def safe_float2_factory(request):
    return request.param
