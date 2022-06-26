from io import BytesIO
import pytest


@pytest.fixture
def iostream():
    return BytesIO()
