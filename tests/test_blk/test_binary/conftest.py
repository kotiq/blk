from io import BytesIO
from pytest import fixture


@fixture
def iostream():
    return BytesIO()
