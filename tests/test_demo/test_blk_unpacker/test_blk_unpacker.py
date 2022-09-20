from shutil import copy
from pathlib import Path
from pexpect import EOF, spawn
from pytest import fixture
from helpers import make_tmppath
import blk.demo as demo
import samples

tmppath = make_tmppath(__name__)
samples_root = Path(samples.__path__[0])
demo_root = Path(demo.__path__[0])
unpacker_py = demo_root / 'blk_unpacker.py'
section_text = (samples_root / 'section_strict.blk').read_text()


@fixture(scope='module')
def single_aut(tmppath):
    dst_root = tmppath / 'single_aut'
    dst_root.mkdir(parents=True, exist_ok=True)
    name = 'section_fat.blk'
    copy(samples_root / name, dst_root / name)
    return dst_root


@fixture(scope='module')
def multiple_aut(tmppath):
    dst_root = tmppath / 'multiple_aut'
    dst_root.mkdir(parents=True, exist_ok=True)
    for name in ('section_bbf.blk', 'section_fat.blk', 'section_fat_zst.blk'):
        copy(samples_root / name, dst_root / name)
    return dst_root


@fixture(scope='module')
def multiple_non_aut_nm(tmppath):
    dst_root = tmppath / 'multiple_non_aut_nm'
    dst_root.mkdir(parents=True, exist_ok=True)
    for name in ('section_slim.blk', 'section_slim_zst.blk'):
        copy(samples_root / name, dst_root / name)
    dst_nm_root = tmppath / 'multiple_non_aut_nm_nm'
    dst_nm_root.mkdir(parents=True, exist_ok=True)
    name = 'nm'
    copy(samples_root / name, dst_nm_root / name)
    return dst_root, dst_nm_root


@fixture(scope='module')
def single_non_aut_nm_dict(tmppath):
    dst_root = tmppath / 'single_non_aut_nm_dict'
    dst_root.mkdir(parents=True, exist_ok=True)
    name = 'section_slim_zst_dict.blk'
    copy(samples_root / name, dst_root / name)
    dst_nm_root = tmppath / 'single_non_aut_nm_dict_nm'
    dst_nm_root.mkdir(parents=True, exist_ok=True)
    name = 'nm'
    copy(samples_root / name, dst_nm_root / name)
    dst_dict_root = tmppath / 'single_non_aut_nm_dict_dict'
    dst_dict_root.mkdir(parents=True, exist_ok=True)
    name = 'bfb732560ad45234690acad246d7b14c2f25ad418a146e5e7ef68ba3386a315c.dict'
    copy(samples_root / name, dst_dict_root / name)
    return dst_root, dst_nm_root, dst_dict_root


@fixture(scope='module')
def tree(tmppath):
    dst_root = tmppath / 'tree'
    aut_root = dst_root / 'aut'
    non_aut_root = dst_root / 'non_aut'
    for path in (aut_root, non_aut_root):
        path.mkdir(parents=True, exist_ok=True)
    for name in ('section_bbf.blk', 'section_fat.blk', 'section_fat_zst.blk'):
        copy(samples_root / name, aut_root / name)
    for name in ('section_slim.blk', 'section_slim_zst.blk', 'section_slim_zst_dict.blk'):
        copy(samples_root / name, non_aut_root / name)
    for name in ('nm', 'bfb732560ad45234690acad246d7b14c2f25ad418a146e5e7ef68ba3386a315c.dict'):
        copy(samples_root / name, dst_root / name)
    return dst_root


"""
1663666795.322609 INFO Начало распаковки.
1663666795.323829 DEBUG '/tmp/pytest-of-kotiq/pytest-12/test_demo.test_blk_unpacker.test_blk_unpacker0/single_aut/section_fat.blk': FAT => STRICT_BLK
1663666795.323961 INFO [ OK ] '/tmp/pytest-of-kotiq/pytest-12/test_demo.test_blk_unpacker.test_blk_unpacker0/single_aut/section_fat.blk'
1663666795.324011 INFO Успешно распаковано: 1/1
"""


def test_unpack_single_aut(single_aut):
    """Одиночный автономный файл."""

    target_root = single_aut.with_name(single_aut.name + '_u')
    name = 'section_fat.blk'
    source = single_aut / name
    cmdline = f'python {unpacker_py} --loglevel debug --format strict_blk -o {target_root} {source}'
    source_repr = repr(str(source))
    with spawn(cmdline, encoding='utf-8') as pipe:
        pipe.expect(
            r'\d+\.\d{6} INFO Начало распаковки\.\r\n'
            r'\d+\.\d{6}'
        )
        pipe.expect_exact(f' DEBUG {source_repr}: FAT => STRICT_BLK\r\n')
        pipe.expect(r'\d+\.\d{6}')
        pipe.expect_exact(f' INFO [ OK ] {source_repr}\r\n')
        pipe.expect(r'\d+\.\d{6} INFO Успешно распаковано: 1/1\r\n')
        pipe.expect(EOF)
    assert pipe.exitstatus == 0
    target = target_root / name
    assert target.is_file()
    assert target.read_text() == section_text


"""
1663682713.904830 INFO Начало распаковки.
1663682713.906617 DEBUG '/tmp/pytest-of-kotiq/pytest-58/test_demo.test_blk_unpacker.test_blk_unpacker0/multiple_out/section_bbf.blk': BBF => STRICT_BLK
1663682713.906752 INFO [ OK ] '/tmp/pytest-of-kotiq/pytest-58/test_demo.test_blk_unpacker.test_blk_unpacker0/multiple_out/section_bbf.blk'
1663682713.907792 DEBUG '/tmp/pytest-of-kotiq/pytest-58/test_demo.test_blk_unpacker.test_blk_unpacker0/multiple_out/section_fat.blk': FAT => STRICT_BLK
1663682713.907912 INFO [ OK ] '/tmp/pytest-of-kotiq/pytest-58/test_demo.test_blk_unpacker.test_blk_unpacker0/multiple_out/section_fat.blk'
1663682713.909169 DEBUG '/tmp/pytest-of-kotiq/pytest-58/test_demo.test_blk_unpacker.test_blk_unpacker0/multiple_out/section_fat_zst.blk': FAT_ZST => STRICT_BLK
1663682713.909310 INFO [ OK ] '/tmp/pytest-of-kotiq/pytest-58/test_demo.test_blk_unpacker.test_blk_unpacker0/multiple_out/section_fat_zst.blk'
1663682713.909353 INFO Успешно распаковано: 3/3
"""


def test_unpack_multiple_aut(multiple_aut):
    """Директория с автономными файлами."""

    target_root = multiple_aut.with_name(multiple_aut.name + '_u')
    cmdline = f'python {unpacker_py} --loglevel debug --format strict_blk -o {target_root} {multiple_aut}'
    name_format_map = {
        'section_bbf.blk': 'BBF',
        'section_fat.blk': 'FAT',
        'section_fat_zst.blk': 'FAT_ZST',
    }
    with spawn(cmdline, encoding='utf-8') as pipe:
        pipe.expect(r'\d+\.\d{6} INFO Начало распаковки\.\r\n')
        for name, format_ in name_format_map.items():
            source = multiple_aut / name
            source_repr = repr(str(source))
            pipe.expect(r'\d+\.\d{6}')
            pipe.expect_exact(f' DEBUG {source_repr}: {format_} => STRICT_BLK\r\n')
            pipe.expect(r'\d+\.\d{6}')
            pipe.expect_exact(f' INFO [ OK ] {source_repr}\r\n')
        pipe.expect(r'\d+\.\d{6} INFO Успешно распаковано: 3/3\r\n')
        pipe.expect(EOF)
    assert pipe.exitstatus == 0
    for name in name_format_map:
        target = target_root / name
        assert target.is_file()
        assert target.read_text() == section_text


"""
1663694060.562330 DEBUG Разделяемая карта имен c2fa9ef840fa12f9
1663688094.797243 DEBUG Ожидаемое имя словаря: bfb732560ad45234690acad246d7b14c2f25ad418a146e5e7ef68ba3386a315c.dict
1663688094.797279 DEBUG Загружена разделяемая карта имен: '/tmp/pytest-of-kotiq/pytest-65/test_demo.test_blk_unpacker.test_blk_unpacker0/multiple_out_nm/nm'
1663688094.797319 INFO Начало распаковки.
1663688094.798733 DEBUG '/tmp/pytest-of-kotiq/pytest-65/test_demo.test_blk_unpacker.test_blk_unpacker0/multiple_out/section_slim.blk': SLIM => STRICT_BLK
1663688094.798891 INFO [ OK ] '/tmp/pytest-of-kotiq/pytest-65/test_demo.test_blk_unpacker.test_blk_unpacker0/multiple_out/section_slim.blk'
1663688094.799837 DEBUG '/tmp/pytest-of-kotiq/pytest-65/test_demo.test_blk_unpacker.test_blk_unpacker0/multiple_out/section_slim_zst.blk': SLIM_ZST => STRICT_BLK
1663688094.799968 INFO [ OK ] '/tmp/pytest-of-kotiq/pytest-65/test_demo.test_blk_unpacker.test_blk_unpacker0/multiple_out/section_slim_zst.blk'
1663688094.800007 INFO Успешно распаковано: 2/2
"""


def test_unpack_multiple_non_aut_nm(multiple_non_aut_nm):
    """Директория с неавтономными файлами с явным указанием карты имен."""

    multiple_non_aut, nm_root = multiple_non_aut_nm
    target_root = multiple_non_aut.with_name(multiple_non_aut.name + '_u')
    nm = nm_root / 'nm'
    cmdline = f'python {unpacker_py} --loglevel debug --format strict_blk --nm {nm} -o {target_root} {multiple_non_aut}'
    name_format_map = {
        'section_slim.blk': 'SLIM',
        'section_slim_zst.blk': 'SLIM_ZST',
    }
    with spawn(cmdline, encoding='utf-8') as pipe:
        pipe.expect(
            r'\d+\.\d{6} DEBUG Разделяемая карта имен [\da-f]{16}\r\n'
            r'\d+\.\d{6} DEBUG Ожидаемое имя словаря: [\da-f]{64}\.dict\r\n'
            r'\d+\.\d{6}'
        )
        pipe.expect_exact(f' DEBUG Загружена разделяемая карта имен: {str(nm)!r}\r\n')
        pipe.expect(r'\d+\.\d{6}')
        pipe.expect_exact(' INFO Начало распаковки.\r\n')
        for name, format_ in name_format_map.items():
            source = multiple_non_aut / name
            source_repr = repr(str(source))
            pipe.expect(r'\d+\.\d{6}')
            pipe.expect_exact(f' DEBUG {source_repr}: {format_} => STRICT_BLK\r\n')
            pipe.expect(r'\d+\.\d{6}')
            pipe.expect_exact(f' INFO [ OK ] {source_repr}\r\n')
        pipe.expect(EOF)
    assert pipe.exitstatus == 0
    for name in name_format_map:
        target = target_root / name
        assert target.is_file()
        assert target.read_text() == section_text


"""
1663692333.985398 DEBUG Загружен словарь: '/tmp/pytest-of-kotiq/pytest-74/test_demo.test_blk_unpacker.test_blk_unpacker0/single_non_aut_nm_dict_dict/bfb732560ad45234690acad246d7b14c2f25ad418a146e5e7ef68ba3386a315c.dict'
1663692333.985716 DEBUG Разделяемая карта имен c2fa9ef840fa12f9
1663692333.985758 DEBUG Ожидаемое имя словаря: bfb732560ad45234690acad246d7b14c2f25ad418a146e5e7ef68ba3386a315c.dict
1663692333.985808 DEBUG Загружена разделяемая карта имен: '/tmp/pytest-of-kotiq/pytest-74/test_demo.test_blk_unpacker.test_blk_unpacker0/single_non_aut_nm_dict_nm/nm'
1663692333.985843 INFO Начало распаковки.
1663692333.987032 DEBUG '/tmp/pytest-of-kotiq/pytest-74/test_demo.test_blk_unpacker.test_blk_unpacker0/single_non_aut_nm_dict/section_slim_zst_dict.blk': SLIM_ZST_DICT => STRICT_BLK
1663692333.987170 INFO [ OK ] '/tmp/pytest-of-kotiq/pytest-74/test_demo.test_blk_unpacker.test_blk_unpacker0/single_non_aut_nm_dict/section_slim_zst_dict.blk'
1663692333.987210 INFO Успешно распаковано: 1/1
"""


def test_unpack_single_non_aut_nm_dict(single_non_aut_nm_dict):
    """Одиночный автономный файл с явным указанием карты имен и словаря."""

    single_non_aut, nm_root, dict_root = single_non_aut_nm_dict
    target_root = single_non_aut.with_name(single_non_aut.name + '_u')
    name = 'section_slim_zst_dict.blk'
    source = single_non_aut / name
    nm = nm_root / 'nm'
    dict_ = dict_root / 'bfb732560ad45234690acad246d7b14c2f25ad418a146e5e7ef68ba3386a315c.dict'
    cmdline = f'python {unpacker_py} --loglevel debug --format strict_blk ' \
              f'--nm {nm} --dict {dict_} -o {target_root} {source}'
    source_repr = repr(str(source))
    with spawn(cmdline, encoding='utf-8') as pipe:
        pipe.expect(r'\d+\.\d{6}')
        pipe.expect_exact(f' DEBUG Загружен словарь: {str(dict_)!r}\r\n')
        pipe.expect(
            r'\d+\.\d{6} DEBUG Разделяемая карта имен [\da-f]{16}\r\n'
            r'\d+\.\d{6} DEBUG Ожидаемое имя словаря: [\da-f]{64}\.dict\r\n'
            r'\d+\.\d{6}'
        )
        pipe.expect_exact(f' DEBUG Загружена разделяемая карта имен: {str(nm)!r}\r\n')
        pipe.expect(r'\d+\.\d{6}')
        pipe.expect_exact(' INFO Начало распаковки.\r\n')
        pipe.expect_exact(f' DEBUG {source_repr}: SLIM_ZST_DICT => STRICT_BLK\r\n')
        pipe.expect(r'\d+\.\d{6}')
        pipe.expect_exact(f' INFO [ OK ] {source_repr}\r\n')
        pipe.expect(r'\d+\.\d{6} INFO Успешно распаковано: 1/1\r\n')
        pipe.expect(EOF)
    assert pipe.exitstatus == 0
    target = target_root / name
    assert target.is_file()
    assert target.read_text() == section_text


"""
1663697611.437401 INFO Начало распаковки.
1663697611.438988 DEBUG '/tmp/pytest-of-kotiq/pytest-86/test_demo.test_blk_unpacker.test_blk_unpacker0/tree/aut/section_bbf.blk': BBF => STRICT_BLK
1663697611.439125 INFO [ OK ] '/tmp/pytest-of-kotiq/pytest-86/test_demo.test_blk_unpacker.test_blk_unpacker0/tree/aut/section_bbf.blk'
1663697611.440354 DEBUG '/tmp/pytest-of-kotiq/pytest-86/test_demo.test_blk_unpacker.test_blk_unpacker0/tree/aut/section_fat.blk': FAT => STRICT_BLK
1663697611.440510 INFO [ OK ] '/tmp/pytest-of-kotiq/pytest-86/test_demo.test_blk_unpacker.test_blk_unpacker0/tree/aut/section_fat.blk'
1663697611.440908 DEBUG Загружен словарь: '/tmp/pytest-of-kotiq/pytest-86/test_demo.test_blk_unpacker.test_blk_unpacker0/tree/bfb732560ad45234690acad246d7b14c2f25ad418a146e5e7ef68ba3386a315c.dict'
1663697611.441790 DEBUG '/tmp/pytest-of-kotiq/pytest-86/test_demo.test_blk_unpacker.test_blk_unpacker0/tree/aut/section_fat_zst.blk': FAT_ZST => STRICT_BLK
1663697611.441915 INFO [ OK ] '/tmp/pytest-of-kotiq/pytest-86/test_demo.test_blk_unpacker.test_blk_unpacker0/tree/aut/section_fat_zst.blk'
1663697611.442232 DEBUG Разделяемая карта имен c2fa9ef840fa12f9
1663697611.442271 DEBUG Ожидаемое имя словаря: bfb732560ad45234690acad246d7b14c2f25ad418a146e5e7ef68ba3386a315c.dict
1663697611.442344 DEBUG Загружена разделяемая карта имен: '/tmp/pytest-of-kotiq/pytest-86/test_demo.test_blk_unpacker.test_blk_unpacker0/tree/nm'
1663697611.443118 DEBUG '/tmp/pytest-of-kotiq/pytest-86/test_demo.test_blk_unpacker.test_blk_unpacker0/tree/non_aut/section_slim.blk': SLIM => STRICT_BLK
1663697611.443227 INFO [ OK ] '/tmp/pytest-of-kotiq/pytest-86/test_demo.test_blk_unpacker.test_blk_unpacker0/tree/non_aut/section_slim.blk'
1663697611.444221 DEBUG '/tmp/pytest-of-kotiq/pytest-86/test_demo.test_blk_unpacker.test_blk_unpacker0/tree/non_aut/section_slim_zst.blk': SLIM_ZST => STRICT_BLK
1663697611.444333 INFO [ OK ] '/tmp/pytest-of-kotiq/pytest-86/test_demo.test_blk_unpacker.test_blk_unpacker0/tree/non_aut/section_slim_zst.blk'
1663697611.445267 DEBUG '/tmp/pytest-of-kotiq/pytest-86/test_demo.test_blk_unpacker.test_blk_unpacker0/tree/non_aut/section_slim_zst_dict.blk': SLIM_ZST_DICT => STRICT_BLK
1663697611.445383 INFO [ OK ] '/tmp/pytest-of-kotiq/pytest-86/test_demo.test_blk_unpacker.test_blk_unpacker0/tree/non_aut/section_slim_zst_dict.blk'
1663697611.445433 INFO Успешно распаковано: 6/6
"""


def test_unpack_tree(tree):
    """Дерево с картой имен и словарем в корне."""

    target_root = tree.with_name(tree.name + '_u')
    cmdline = f'python {unpacker_py} --loglevel debug --format strict_blk -o {target_root} {tree}'
    aut_name_format_map = {
        'section_bbf.blk': 'BBF',
        'section_fat.blk': 'FAT',
        'section_fat_zst.blk': 'FAT_ZST',
    }
    non_aut_format_map = {
        'section_slim.blk': 'SLIM',
        'section_slim_zst.blk': 'SLIM_ZST',
        'section_slim_zst_dict.blk': 'SLIM_ZST_DICT',
    }
    nm = tree / 'nm'
    dict_ = tree / 'bfb732560ad45234690acad246d7b14c2f25ad418a146e5e7ef68ba3386a315c.dict'
    aut_root = tree / 'aut'
    non_aut_root = tree / 'non_aut'
    with spawn(cmdline, encoding='utf-8') as pipe:
        pipe.expect(r'\d+\.\d{6} INFO Начало распаковки\.\r\n')
        for name, format_ in aut_name_format_map.items():
            source = aut_root / name
            source_repr = repr(str(source))
            if format_ == 'FAT_ZST':
                pipe.expect(r'\d+\.\d{6}')
                pipe.expect_exact(f' DEBUG Загружен словарь: {str(dict_)!r}\r\n')
            pipe.expect(r'\d+\.\d{6}')
            pipe.expect_exact(f' DEBUG {source_repr}: {format_} => STRICT_BLK\r\n')
            pipe.expect(r'\d+\.\d{6}')
            pipe.expect_exact(f' INFO [ OK ] {source_repr}\r\n')
        pipe.expect(
            r'\d+\.\d{6} DEBUG Разделяемая карта имен [\da-f]{16}\r\n'
            r'\d+\.\d{6} DEBUG Ожидаемое имя словаря: [\da-f]{64}\.dict\r\n'
            r'\d+\.\d{6}'
        )
        pipe.expect_exact(f' DEBUG Загружена разделяемая карта имен: {str(nm)!r}\r\n')
        for name, format_ in non_aut_format_map.items():
            source = non_aut_root / name
            source_repr = repr(str(source))
            pipe.expect(r'\d+\.\d{6}')
            pipe.expect_exact(f' DEBUG {source_repr}: {format_} => STRICT_BLK\r\n')
            pipe.expect(r'\d+\.\d{6}')
            pipe.expect_exact(f' INFO [ OK ] {source_repr}\r\n')
        pipe.expect(r'\d+\.\d{6} INFO Успешно распаковано: 6/6\r\n')
        pipe.expect(EOF)
    assert pipe.exitstatus == 0
    for (map_, sub) in [(aut_name_format_map, 'aut'), (non_aut_format_map, 'non_aut')]:
        for name in map_:
            target = target_root / sub / name
            assert target.is_file()
            assert target.read_text() == section_text
