import pytest
from blk.types import LineComment


def test_of(line_comment, line_comment_value):
    assert LineComment.of(line_comment_value) == line_comment


@pytest.mark.parametrize('text', [
    pytest.param('line\rcomment', id='CR'),
    pytest.param('line\ncomment', id='LF'),
])
def test_of_text_contains_newline_raises_ValueError(text):
    with pytest.raises(ValueError):
        LineComment.of(text)
