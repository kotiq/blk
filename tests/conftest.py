from pathlib import Path
import pytest


def pytest_addoption(parser):
    currespath = {
        'name': 'currespath',
        'help': 'Директория с образцами двоичных blk текущего формата.',
    }

    bbfrespath = {
        'name': 'bbfrespath',
        'help': 'Директория с образцами двоичных blk фрмата BBF3.'
    }

    buildpath = {
        'name': 'buildpath',
        'help': 'Директория для построения тестами.'
    }
    cdkpath = {
        'name': 'cdkpath',
        'help': 'Директория WarThunderCDK.'
    }
    for m in currespath, bbfrespath, buildpath, cdkpath:
        parser.addini(**m)


@pytest.fixture(scope='session')
def currespath(pytestconfig):
    return Path(pytestconfig.getini('currespath'))


@pytest.fixture(scope='session')
def bbfrespath(pytestconfig):
    return Path(pytestconfig.getini('bbfrespath'))


@pytest.fixture(scope='session')
def buildpath(pytestconfig):
    return Path(pytestconfig.getini('buildpath'))


@pytest.fixture(scope='session')
def cdkpath(pytestconfig):
    return Path(pytestconfig.getini('cdkpath'))
