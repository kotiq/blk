import os


def outdir_rpath(name):
    return os.path.join('tests', *name.split('.'))
