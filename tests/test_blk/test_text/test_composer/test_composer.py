from pathlib import Path
from pytest import fail, mark, param as _, skip
from pytest_lazyfixture import lazy_fixture
from blk.text.error import ComposeError
from blk.text.composer import compose

expect_failed = {Path(k): v for k, v in {
    'develop/assets/entities/buildings/pyrenees/city_buildings/pyrenees_city_j_cmp.composit.blk': '62: Запятая как разделитель параметров',
    'develop/assets/entities/destructible_assets/power_pole/tram_pole_concrete_b_cmp.composit.blk': '18: Запятая как разделитель дробной части',
    'develop/assets/entities/fortifications/trenches/vlaanderen/sub_composits/trench_long_a_sandbags_a_random.composit.blk': '42: пробел в записи числа',
    'develop/assets/landclasses/air_vs_ground_detailed/avg_vlaanderen/avg_vlaanderen_detailed_biome.land.blk': '213: запятая как разделитель дробной части',
    'develop/assets/splines_n_lands/slope/red_sandstone_big_rock_border_a.spline.blk': '27: запятая как разделитель дробной части',
}.items()}


@mark.parametrize('path', [
    _(lazy_fixture('cdkpath'), id='cdk'),
])
def test_compose_no_actions(path: Path):
    if not (path.exists() and path.is_dir()):
        skip('Не директория.')

    failed = []

    for p in path.rglob('*.blk'):
        rel_p = p.relative_to(path)
        if rel_p in expect_failed:
            reason = expect_failed[rel_p]
            print('[SKIP] text {!r}: {}'.format(str(p), reason))
        else:
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
                    failed.append((str(p), e))
                    break

            if section is None:
                print('[SKIP] binary {!r}'.format(str(p)))
            else:
                print('[OK] text {!r}'.format(str(p)))

    if expect_failed:
        print('\nExpected failed files:')
        for p, reason in expect_failed.items():
            print(f'{p}: {reason}')

    if failed:
        print('\nFailed files:')
        for p, e in failed:
            print(f'{p}: {e}: {e.__cause__}')
        fail(pytrace=False)
