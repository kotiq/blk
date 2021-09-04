import pytest


def pytest_addoption(parser):
    binrespath = {
        'name': 'binrespath',
        'help': 'Директория с образцами двоичных blk.',
    }
    buildpath = {
        'name': 'buildpath',
        'help': 'Директория для построения тестами.'
    }
    cdkpath = {
        'name': 'cdkpath',
        'help': 'Директория WarThunderCDK.'
    }
    for m in binrespath, buildpath, cdkpath:
        parser.addini(**m)


@pytest.fixture(scope='session')
def binrespath(pytestconfig):
    return pytestconfig.getini('binrespath')


@pytest.fixture(scope='session')
def buildpath(pytestconfig):
    return pytestconfig.getini('buildpath')


@pytest.fixture(scope='session')
def cdkpath(pytestconfig):
    return pytestconfig.getini('cdkpath')
