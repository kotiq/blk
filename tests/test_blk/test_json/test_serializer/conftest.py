from textwrap import dedent
import pytest
from blk.types import DictSection, Float, Float12, Name, Str


@pytest.fixture(scope='module')
def json():
    text = """\
    [
      {
        "entity": {
          "_template": "level",
          "level.bin": "content/pkg_dev/levels/hangar_field.bin",
          "level.weather": "hazy",
          "level.environment": "night"
        }
      },
      {
        "entity": {
          "_template": "way_point",
          "way_point.transform": [
            [1.0,0.0,0.0],
            [0.0,1.0,0.0],
            [0.0,0.0,1.0],
            [14.74,46.53,-625.89]
          ],
          "waypoint.name": "wp_01",
          "way_point.moveType": "MOVE_TO_STRAIGHT",
          "way_point.speed": 30.0
        }
      },
      {
        "entity": {
          "_template": "route",
          "route.routeId": "route_01",
          "route.wayPointsNames:list<t>": [
            {
              "n": "wp_01"
            },
            {
              "n": "wp_02"
            }
          ]
        }
      }
    ]"""
    return dedent(text)


@pytest.fixture(scope='module')
def json_2():
    text = """\
    {
      "entity": [
        {
          "_template": [
            "level"
          ],
          "level.bin": [
            "content/pkg_dev/levels/hangar_field.bin"
          ],
          "level.weather": [
            "hazy"
          ],
          "level.environment": [
            "night"
          ]
        },
        {
          "_template": [
            "way_point"
          ],
          "way_point.transform": [
            [
              [1.0,0.0,0.0],
              [0.0,1.0,0.0],
              [0.0,0.0,1.0],
              [14.74,46.53,-625.89]
            ]
          ],
          "waypoint.name": [
            "wp_01"
          ],
          "way_point.moveType": [
            "MOVE_TO_STRAIGHT"
          ],
          "way_point.speed": [
            30.0
          ]
        },
        {
          "_template": [
            "route"
          ],
          "route.routeId": [
            "route_01"
          ],
          "route.wayPointsNames:list<t>": [
            {
              "n": [
                "wp_01",
                "wp_02"
              ]
            }
          ]
        }
      ]
    }"""
    return dedent(text)


@pytest.fixture(scope='module')
def json_3():
    text = """\
    {
      "entity": [
        {
          "_template": "level",
          "level.bin": "content/pkg_dev/levels/hangar_field.bin",
          "level.weather": "hazy",
          "level.environment": "night"
        },
        {
          "_template": "way_point",
          "way_point.transform": [
            [1.0,0.0,0.0],
            [0.0,1.0,0.0],
            [0.0,0.0,1.0],
            [14.74,46.53,-625.89]
          ],
          "waypoint.name": "wp_01",
          "way_point.moveType": "MOVE_TO_STRAIGHT",
          "way_point.speed": 30.0
        },
        {
          "_template": "route",
          "route.routeId": "route_01",
          "route.wayPointsNames:list<t>": {
            "n": [
              "wp_01",
              "wp_02"
            ]
          }
        }
      ]
    }"""
    return dedent(text)


@pytest.fixture(scope='module')
def dict_section():
    root = DictSection()
    entity0 = DictSection()
    entity1 = DictSection()
    entity2 = DictSection()

    entity0.append((Name('_template'), Str('level')))
    entity0.append((Name('level.bin'), Str('content/pkg_dev/levels/hangar_field.bin')))
    entity0.append((Name('level.weather'), Str('hazy'))),
    entity0.append((Name('level.environment'), Str('night')))

    entity1.append((Name('_template'), Str('way_point')))
    entity1.append((Name('way_point.transform'),
                    Float12((1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 14.74, 46.53, -625.89))))
    entity1.append((Name('waypoint.name'), Str('wp_01')))
    entity1.append((Name('way_point.moveType'), Str('MOVE_TO_STRAIGHT')))
    entity1.append((Name('way_point.speed'), Float(30.0)))

    entity2.append((Name('_template'), Str('route')))
    entity2.append((Name('route.routeId'), Str('route_01')))

    names = DictSection()
    names.append((Name('n'), Str('wp_01')))
    names.append((Name('n'), Str('wp_02')))
    entity2.append((Name('route.wayPointsNames:list<t>'), names))

    root.append((Name('entity'), entity0))
    root.append((Name('entity'), entity1))
    root.append((Name('entity'), entity2))

    return root
