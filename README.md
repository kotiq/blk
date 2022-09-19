# Вспомогательный инcтрументарий для работы с файлами конфигурации.

## Среда выполнения

Linux, Рython 3.7 для совместимости с PyPy3.

## Установка

```pip install .```

## Сборка документации

Диаграммы построены с использованием [drawio](https://github.com/jgraph/drawio-desktop/)

```
pip install -r requirements-docs.txt
python setup.py build_sphinx
```

## Распаковка файлов

Демонстрационные скрипты находятся в проекте `wt-tools` и работают в паре с распаковщиком `vromfs_unpacker.py` 
указанного проекта. 
Они основаны на `blk_unpacker.py` проекта `wt-tools` и реализуют подобный интерфейс командной строки с форматами 
`strict_blk`, `json`, `json_2`, `json_3`.

`blk_unpack_ng.py` с одним процессом.\
`blk_unpack_ng_mp.py` с числом процессов по количеству ядер.

Другой демонстрационный скрипт `src/blk/demo/blk_unpacker.py`. Он работает в паре с распаковщиком `vromfs_bin_unpacker`
из проекта `vromfs` для разработчика, либо самостоятельно для распаковки автономных файлов.

### Распаковка файлов

```shell
blk_unpacker [--nm NM_PATH] 
             [--dict DICT_PATH] 
             [--format {json,json_2,json_3,raw,strict_blk}] 
             [--sort] 
             [--minify] 
             [-x]
             [-o OUT_PATH] 
             [--flat]
             in_path
```

Аргументы:

- `--nm` Путь карты имен.
- `--dict` Путь словаря.
- `--format` Формат выходного блока, не зависит от регистра. По умолчанию `json`.
- `--sort` Сортировать ключи для форматов `json`, `json_2`, `json_3`.
- `--minify` Минифицировать json.
- `-x, --exitfirst` Закончить распаковку при первой ошибке.
- `-o, --output` Выходная директория для распаковки. Если output не указан, выходная директория для распаковки совпадает
со входной, к расширению файлов добавляется 'x'.
- `--flat` Плоская выходная структура.
- `in_path` Путь, содержащий упакованные файлы.

#### Примеры

Распаковка одиночного автономного файла в директорию `/tmp/out`. Формат `json_3`, выход минифицирован.
```shell
blk_unpacker --format=json_3 --minify -o /tmp/out/ \
/home/kotiq/games/linux/WarThunder/cache/content/downloadable_skins.3wus7y73vkqoyfr2g2rdk2e2o5ehkt5w-hv4c.blk
```
```text
1663599383.09862 INFO Начало распаковки.
1663599384.2189617 DEBUG '/home/kotiq/games/linux/WarThunder/cache/content/downloadable_skins.3wus7y73vkqoyfr2g2rdk2e2o5ehkt5w-hv4c.blk': FAT_ZST => JSON_3
1663599384.2219203 INFO Успешно распаковано: 1/1
```

Распаковка всех автономных файлов из директории в директорию `/tmp/out`. Формат `strict_blk`. 
```shell
blk_unpacker --format=strict_blk -o /tmp/out/ /home/kotiq/games/linux/WarThunder/cache/content/
```
```text
1663599469.160413 INFO Начало распаковки.
1663599470.1330087 DEBUG '/home/kotiq/games/linux/WarThunder/cache/content/downloadable_decals.n6644yww4hqvhx6ia4vput3k3khwsrep-fcr2.blk': FAT_ZST => STRICT_BLK
1663599471.0740328 DEBUG '/home/kotiq/games/linux/WarThunder/cache/content/downloadable_decals.hzk3bnebxl524ig2zpxj6sv42ovubhaf-fcrh.blk': FAT_ZST => STRICT_BLK
1663599472.0435433 DEBUG '/home/kotiq/games/linux/WarThunder/cache/content/downloadable_decals.5c2pd54ox47uhvvnnjc4uli36mel5s4e-fcx4.blk': FAT_ZST => STRICT_BLK
...
1663599531.63824 INFO Успешно распаковано: 58/58
```

##### Для разработчика
Распаковка дерева файлов, в том числе неавтономных, в директорию `/tmp/out/char`. Формат `strict_blk`.
Карта имен и словарь находятся в корне дерева.
```shell
blk_unpacker --format=strict_blk -o /tmp/out/char /home/kotiq/games/resources/all/WarThunder-RAW/char.vromfs.bin
```
```text
1663600090.7580874 INFO Начало распаковки.
1663600090.829308 DEBUG Разделяемая карта имен 17fa000ef47a148b
1663600094.244224 DEBUG '/home/kotiq/games/resources/all/WarThunder-RAW/char.vromfs.bin/config/wpcost.blk': SLIM_ZST => STRICT_BLK
1663600094.259905 DEBUG '/home/kotiq/games/resources/all/WarThunder-RAW/char.vromfs.bin/config/warpoints.blk': SLIM_ZST => STRICT_BLK
1663600094.834506 DEBUG '/home/kotiq/games/resources/all/WarThunder-RAW/char.vromfs.bin/config/unlocks.blk': SLIM_ZST => STRICT_BLK
...
1663600096.0535452 INFO Успешно распаковано: 21/21
```

##### Для разработчика
Распаковка одиночного неавтономного файла в директорию `/tmp/out`. Формат `strict_blk`.
Карта имен и словарь указаны явно.
```shell
blk_unpacker --format=strict_blk -o /tmp/out/ \
--nm /home/kotiq/games/resources/all/WarThunder-RAW/aces.vromfs.bin/nm \
--dict /home/kotiq/games/resources/all/WarThunder-RAW/aces.vromfs.bin/3d2907d0e7420dc093d67430955a607a2f467f1b79e0bea4aec49f6a9c2e4c71.dict \
/home/kotiq/games/resources/all/WarThunder-RAW/aces.vromfs.bin/config/camera.blk
```
```text
1663602355.3463955 DEBUG Загружен словарь: '/home/kotiq/games/resources/all/WarThunder-RAW/aces.vromfs.bin/3d2907d0e7420dc093d67430955a607a2f467f1b79e0bea4aec49f6a9c2e4c71.dict'
1663602355.6206803 DEBUG Разделяемая карта имен 29213f4758054e3e
1663602355.6208432 DEBUG Ожидаемое имя словаря: 3d2907d0e7420dc093d67430955a607a2f467f1b79e0bea4aec49f6a9c2e4c71.dict
1663602355.6209748 INFO Начало распаковки.
1663602355.850776 DEBUG '/home/kotiq/games/resources/all/WarThunder-RAW/aces.vromfs.bin/config/camera.blk': SLIM_ZST_DICT => STRICT_BLK
1663602355.8511212 INFO Успешно распаковано: 1/1
```

### Выходные форматы

#### strict_blk

Результат обхода секции в глубину с сохранением типов. Для форматов `json*` потребуется схема для полного
восстановления секции.

<table>
<tr>
<th>Отображение</th>
<th>Мультиотображение</th>
</tr>
<tr>
<td valign="top">

```
// single_map-strict_blk.txt

a:i=1
b:i=2
c:i=3

sub{
  x:r=4.0
  y:r=5.0
}
```

</td>
<td valign="top">

```
// multi_map-strict_blk.txt

a:i=1
a:i=2
b:i=3

sub{
  x:r=4.0
  y:r=5.0
}
```

</td>
</tr>
</table>

#### json

Подходит для секций, в которых мультизначение состоит из одного значения.
Иначе контейнер из словаря превратится в список словарей на уровне мультизначения.

<table>
<tr>
<th>Отображение</th>
<th>Мультиотображение</th>
</tr>
<tr>
<td valign="top">

```json5
// single_map-json.json

{
  "a": 1,
  "b": 2,
  "c": 3,
  "sub": {
    "x": 4.0,
    "y": 5.0
  }
}
```

</td>
<td valign="top">

```json5
// multi_map-json.json

[
  {
    "a": 1
  },
  {
    "a": 2
  },
  {
    "b": 3
  },
  {
    "sub": {
      "x": 4.0,
      "y": 5.0
    }
  }
]
```

</td>
</tr>
</table>

#### json_2

Каждое мультизначение представлено списком значений.

<table>
<tr>
<th>Отображение</th>
<th>Мультиотображение</th>
</tr>
<tr>
<td valign="top">

```json5
// single_map-json_2.json

{
  "a": [
    1
  ],
  "b": [
    2
  ],
  "c": [
    3
  ],
  "sub": [
    {
      "x": [
        4.0
      ],
      "y": [
        5.0
      ]
    }
  ]
}
```

</td>
<td valign="top">

```json5
// multi_map-json_2.json

{
  "a": [
    1,
    2
  ],
  "b": [
    3
  ],
  "sub": [
    {
      "x": [
        4.0
      ],
      "y": [
        5.0
      ]
    }
  ]
}
```

</td>
</tr>
</table>



#### json_3

Мультизначение с одним значением представлено одним значением.
Мультизначение с несколькими значениями представлено списком значений.

<table>
<tr>
<th>Отображение</th>
<th>Мультиотображение</th>
</tr>
<tr>
<td valign="top">

```json5
// single_map-json_3.json

{
  "a": 1,
  "b": 2,
  "c": 3,
  "sub": {
    "x": 4.0,
    "y": 5.0
  }
}
```

</td>
<td valign="top">

```json5
// multi_map-json_3.json

{
  "a": [
    1,
    2
  ],
  "b": 3,
  "sub": {
    "x": 4.0,
    "y": 5.0
  }
}
```

</td>
</tr>
</table>

## Особенности реализации

Инструмент основан на представлении секции как `{name: [values]}`.

```
[(a, x), (b, y), (a, z)] -> {a: [x, z], b: [y]}
```

Секция запоминает порядок только первого
значения при добавлении `(name, value)` пары.

```
a -> x
a -> z
b -> y
```

Это может повлечь разрастание разности текстовых файлов, если вы прежде использовали в своих архивах распаковщик,
основанный на представлении секции как `[(name, value)]`, способной запоминать порядок всех пар при добавлении.

```
a -> x
b -> y
a -> z
```

## Тестирование

Настраиваемые директории в `pytest.ini`

* `currespath` директория с файлами `blk` текущего формата
* `bbfrespath` директория с файлами `blk` формата bbf3
* `cdkpath` директория CDK с текстовыми файлами
* `buildpath` выходная директория тестов

После настройки одноименные фикстуры для `pytest`содержат указанные пути. 
