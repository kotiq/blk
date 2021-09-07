import os
import pytest


@pytest.fixture(scope='session')
def bbfpath(binrespath):
    return os.path.join(binrespath, 'bbf')