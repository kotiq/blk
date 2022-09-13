import parsy as ps
import pytest
from pytest import param as _, raises
from blk.types import Include
from blk.text.composer import include


@pytest.mark.parametrize(['text', 'item'], [
    _('include file.blk', Include('file.blk'), id='unquoted'),
    _('include "file.blk"', Include('file.blk'), id='quoted'),
    _('include "common/file.blk"', Include('common/file.blk'), id='slash'),
    _('include "common\\file.blk"', Include('common/file.blk'), id='back slash'),
    _('include "common\\city/file.blk"', Include('common/city/file.blk'), id='mixed slash'),
    _('include "#/file.blk"', Include('#/file.blk'), id='cdk root'),
    _('include "#file.blk"', Include('#/file.blk'), id='cdk root no sep'),
    _('include ":/file.blk"', Include(':/file.blk'), id='mount root'),
    _('include ":file.blk"', Include(':/file.blk'), id='mount root no sep'),
    _('include "../common/file.blk"', Include('../common/file.blk'), id='parent'),
])
def test_include(text, item):
    parsed = include.parse(text)
    assert isinstance(parsed, Include)
    assert parsed == item


@pytest.mark.parametrize('text', [
    _('include', id='empty'),
    _('include ""', id='quoted empty'),
])
def test_empty_text_raises_ParseError(text):
    with raises(ps.ParseError):
        print(include.parse(text))
