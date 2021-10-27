from setuptools import setup, find_packages

setup(
    name='blk',
    author='kotiq',
    author_email='courier.yeti@gmail.com',
    url='https://github.com/kotiq/blk',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.7',
)
