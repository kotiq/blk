import pytest


def pytest_addoption(parser):
    binrespath = {
        'name': 'binrespath',
        'type': 'string',
        'help': 'Директория с образцами двоичных blk.',
    }
    buildpath = {
        'name': 'buildpath',
        'type': 'string',
        'help': 'Директория для построения тестами.'
    }
    cdkpath = {
        'name': 'cdkpath',
        'type': 'string',
        'help': 'Директория WarThunderCDK.'
    }
    for m in binrespath, buildpath, cdkpath:
        parser.addini(**m)


@pytest.fixture(scope='session')
def binrespath(request):
    return request.config.getini('binrespath')


@pytest.fixture(scope='session')
def buildpath(request):
    return request.config.getini('buildpath')


@pytest.fixture(scope='session')
def cdkpath(request):
    return request.config.getini('cdkpath')
