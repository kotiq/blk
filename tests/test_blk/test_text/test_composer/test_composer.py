from pathlib import Path
import pytest
from pytest import mark, param as _, skip
from pytest_lazyfixture import lazy_fixture
from blk.text.error import ComposeError
from blk.text.composer import compose

expect_fail = {
    Path('develop/assets/splines_n_lands/roads/peleliu_roads.spline.blk'): 'Вложенный блочный комментарий',
    Path('develop/assets/landclasses/air_vs_ground_detailed/avg_karelia_forest_a/ml_karelia_mixed_forest.land.blk'): 'Вложенный блочный комментарий',
}


@mark.parametrize('path', [
    _(lazy_fixture('cdkpath'), id='cdk'),
])
def test_compose_no_actions(path: Path):
    if not (path.exists() and path.is_dir()):
        skip('Не директория.')

    for p in path.rglob('*.blk'):
        rel_p = p.relative_to(path)
        if rel_p in expect_fail:
            reason = expect_fail[rel_p]
            print('[SKIP] text {!r}: {}'.format(str(p), reason))
        else:
            def f():
                encodings = 'utf8', 'cp1251'
                section = None
                for e in encodings:
                    try:
                        with open(p, encoding=e) as istream:
                            section = compose(istream, remove_comments=False, include_files=False)
                            break
                    except UnicodeDecodeError:
                        section = None
                    except ComposeError as e:
                        print('[FAIL] text {!r}: {}'.format(str(p), e))
                        pytest.fail(e.__class__.__name__)
                        return

                if section is None:
                    print('[SKIP] binary {!r}'.format(str(p)))
                else:
                    print('[OK] text {!r}'.format(str(p)))

            f()
