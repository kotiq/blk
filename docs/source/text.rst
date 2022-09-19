===================
Текстовые файлы BLK
===================

Неформально описана упрощенная версия языка текстовых файлов BLK.
Она подходит для большинства текстов из ``WarThunderCDK``.

Пример корневой секции в текстовом файле.

.. code-block:: javascript

    "vec4f":p4 = 1.25, 2.5, 5, 10
        "int":i = 42
        "long":i64 = 0x40
        "alpha" {
          "str":t = "hello"
          "bool":b = true
          "color":c = 0x1, 0x2, 0x3, 0x4
          "gamma" {
            "vec2i":ip2 = 3, 4
            "vec2f":p2 = 1.25, 2.5
            "transform":m = [[1, 0, 0] [0, 1, 0] [0, 0, 1] [1.25, 2.5, 5]]
          }
        }
        "beta" {
          "float":r = 1.25
          "vec2i":ip2 = 1, 2
          "vec3f":p3 = 1.25, 2.5, 5
        }

Отношения между классами сущностей в тексте:

.. drawio-image:: diagrams/text_file_items.drawio

Комментарий (comment)
=====================

.. code-block:: text

    comment = line comment | block comment ;

Место комментария

.. code-block:: text

     name ":" tag "=" parameter value
    ^    ^   ^   ^   ^               ^
     name "{" items "}"
    ^    ^   ^     ^   ^
     include command
    ^               ^

В случае комментария перед или после именованного значения или команды есть возможность его сохранить в упорядоченной
секции в виде специального именованного строкового параметра.

Строчный комментарий (line comment)
===================================

Комментарий С++.

.. code-block:: javascript

    // однострочный комментарий


Блочный комментарий (block comment)
===================================

В файлах встречаются вложенные блочные комментарии.

.. code-block:: javascript

    /* однострочный комментарий */

    /*
    многострочный
    комментарий
    */

Именованное значение (named value)
==================================

.. code-block:: text

    named value = name, value ;

Имя (name)
==========

Строка в двойных или одинарных кавычках или строка без кавычек.
Имя в кавычках может содержать пробельные символы и комплементарные кавычки.

.. code-block:: javascript

    "double quoted 'name'":i = 1
    ^^^^^^^^^^^^^^^^^^^^^^

    'single quoted "name"':i = 2
    ^^^^^^^^^^^^^^^^^^^^^^

    unquoted_name:i = 3
    ^^^^^^^^^^^^^


.. code-block:: text

    name = double quoted string | single quoted string | not quoted string ;

Именованный параметр (named parameter)
======================================

Представляет пару имя-параметр.

.. code-block:: text

    named parameter = name, ":", parameter tag, "=", parameter value ;

.. code-block:: javascript

    "integer":i = 42

Тег параметра (parameter tag)
=============================

Тег параметра определяет тип следующего за ним значения параметра.

.. code-block:: javascript

    name:t = value
         ^
.. code-block:: text

    tag = "i64" | "ip2" | "ip3" | "p2" | "p3" | "p4" | "b" | "t" | "i" | "r" | "c" | "m" ;


.. list-table:: Теги параметра
    :header-rows: 1
    :align: left

    * - Тег
      - Тип значения параметра
    * - b
      - Булево
    * - t
      - Строка
    * - i
      - Целое
    * - i64
      - Длинное целое
    * - r
      - Рациональное
    * - ip2
      - Вектор целых 1x2
    * - ip3
      - Вектор целых 1x3
    * - c
      - Цвет
    * - p2
      - Вектор рациональных 1x2
    * - p3
      - Вектор рациональных 1x3
    * - p4
      - Вектор рациональных 1x4
    * - m
      - Вектор рациональных 4x3

Булево (bool)
=============

Двоичный флаг.

.. code-block:: javascript

    "true":b = true
               ^^^^

    "false":b = 0
                ^

.. code-block:: text

    true = "true" | "yes" | "on" | "1" ;
    false = "false" | "no" | "off" | "0" ;
    boolean = true | false ;

Строка (str)
============

Строка в тройных двойных или одинарных кавычках или строка в двойных или одинарных кавычках или строка без кавычек.
Строка в тройных кавычках может содержать кавычки, экранированные тройные кавычки ``~'''``, ``~"""`` и неэкранированные
пробельные символы.
Строка в кавычках может содержать пробельные символы, экранированные последовательности и комплементарные кавычки.

.. code-block:: javascript

    "triple double quoted string":t = """triple double
                                      ^^^^^^^^^^^^^^^^
    quoted~t string "x" """
    ^^^^^^^^^^^^^^^^^^^^^^^

    "triple single quoted string":t = '''triple single\tquoted ~'''string~''''''
                                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    "double quoted string":t = "double quoted~nstring 'x'"
                               ^^^^^^^^^^^^^^^^^^^^^^^^^^^

    "single quoted string":t = 'single quoted~tstring "y"'
                               ^^^^^^^^^^^^^^^^^^^^^^^^^^^

    "unquoted string":t = unquoted_string
                          ^^^^^^^^^^^^^^^


.. code-block::

    triple quoted string = triple double quoted string | triple single quoted string
    quoted string = double quoted string | single quoted string
    string = triple quoted string | quoted string | unquoted string

.. list-table:: Экранированные последовательности
    :header-rows: 1
    :align: left

    * - blk
      - c
      - Назначение
    * - ``~~``
      - ``~``
      - Тильда
    * - ``~'``
      - ``'``
      - Одинарная кавычка
    * - ``~"``
      - ``"``
      - Двойная кавычка
    * - ``~t``
      - ``\t``
      - Горизонтальная табуляция
    * - ``~n``
      - ``\n``
      - Перенос строки
    * - ``~r``
      - ``\r``
      - Возврат каретки

Прочие символы после ``~``, кроме ``\t``, ``\n``, ``\r``, переходят в себя.

Целое (int)
===========

Знаковое 32-битное десятичное или шестнадцатеричное целое.

.. code-block:: javascript

    "decimal integer":i = -10
                          ^^^

    "hexadecimal integer":i = 0x100
                              ^^^^^

Длинное целое (long)
====================

Знаковое 64-битное десятичное или шестнадцатеричное целое.

.. code-block:: javascript

    "decimal long integer":i64 = -10
                                 ^^^

    "hexadecimal long integer":i64 = 0x100
                                     ^^^^^

Рациональное (float)
====================

Знаковое число с плавающей точкой одинарной точности, исключая бесконечности и не-число.

.. code-block:: javascript

    "int":r = 1
              ^

    "float":r = -1.5
                 ^^^^

    "scientific":r = 3.14e2
                     ^^^^^^

Вектор целых 1x2 (int2)
=======================

Пара целых.

.. code-block:: javascript

    "point2d":ip2 = 1, 2
                    ^^^^

.. code-block:: text

    int2 = int, "," int ;

Вектор целых 1x3 (int3)
=======================

Тройка целых.

.. code-block:: javascript

    "point3d":ip3 = 1, 2, 3
                    ^^^^^^^

.. code-block:: text

    int3 = int, "," int2 ;

Цвет (color)
============

Четверка или тройка беззнаковых 8-битных целых.

.. code-block:: javascript

    "color":c = 255, 0, 0, 127
                ^^^^^^^^^^^^^^

    "color partial":c = 255, 0, 0
                        ^^^^^^^^^

.. code-block:: text


    ubyte3 = ubyte, 2 * { ",", ubyte } ;
    ubyte4 = ubyte, ",", ubyte3 ;
    color = ubyte4 | ubyte3 ;

Вектор рациональных 1x2 (float2)
================================

Пара рациональных.

.. code-block:: javascript

    "point2d":p2 = 1.0, 0.0
                   ^^^^^^^^

.. code-block:: text

    float2 = float, ",", float ;

Вектор рациональных 1x3 (float3)
================================

Тройка рациональных.

.. code-block:: javascript

    "point3d":p3 = 1.0, 0.0, 0.0
                   ^^^^^^^^^^^^^

.. code-block:: text

    float3 = float, ",", float2 ;

Вектор рациональных 1x4 (float4)
================================

Четверка рациональных.

.. code-block:: javascript

    "point4d":p4 = 1.0, 0.0, 0.0, 0.0
                   ^^^^^^^^^^^^^^^^^^

.. code-block:: text

    float4 = float, ",", float3 ;

Вектор рациональных 4x3 (float12)
=================================

Двенадцать рациональных.

.. code-block:: javascript

    "transform":m = [[1, 0, 0] [0, 1, 0] [0, 0, 1] [1.25, 2.5, 5]]
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   float12 = "[", 4 * { "[", float3, "]" }, "]" ;

Специальные именованные параметры
=================================

Специальные именованные параметры служат для представления всех классов элементов секции.

.. list-table:: Специальные имена
    :header-rows: 1
    :align: left

    * - Имя
      - Назначение
    * - ``@commentCPP``
      - Строчный комментарий
    * - ``@commentC``
      - Блочный комментарий
    * - ``@include``
      - Инструкция включения


.. code-block::

    "@commentCPP":t = "line comment"
    "@commentC":t = "multi~nline~ncomment"
    "@include":t = "path/to/file.blk"

.. code-block:: text

    special name = "@", "include" | "commentCPP" | "commentC" ;

    special named parameter =  special name, ":", "t", string ;

Именованная секция (named section)
==================================

Представляет пару имя-секция.

.. code-block:: text

    named section = name, "{", { item }, "}" ;

.. code-block:: javascript

    "section" {
      "integer":i = 42
      "subsection" {
        "float":r = 3.14
      }
    }

Инструкция включения (include)
==============================

Представляет путь к текстовому файлу BLK.

.. code-block:: text

    include = "include", path ;

Разделители пути: ``/`` и ``\``

.. list-table:: Префиксы
    :header-rows: 1
    :widths: 10 90
    :align: left

    * - Префикс
      - Назначение
    * - ``:``
      - Директория ресурсов. Схема монтирования описана в ``WarThunderCDK/application.blk``
    * - ``#``
      - Директория ``WarThunderCDK``

Значения префиксов оканчиваются разделителем пути. Путь без префиксов считается относительно родительской директории
обрабатываемого файла.

.. code-block:: javascript

    include ":/levels/grass_colors/_grass_color_fill_a.blk"
    include "#\develop\assets\landclasses\eastern\kursk\_kursk_trees_color.blk"
    include "#develop/assets/landclasses/air_vs_ground_detailed/avg_mozdok/_mozdok_detailed_tree_colors.blk"
    include "#/develop/assets/landclasses/europe/_britain_tree_colors.blk"
    include "_zhengzhou_tree_colors.blk"
    include "../../landclasses/europe/_berlin_tree_colors.blk"
    include latin.blk

Разделители элементов секции
============================

Разделители элементов секции для случаев смешения имени и значения предыдущего параметра:
значение, кроме bool и float12, и имя без кавычек или инструкция включения;


.. code-block:: text

    optional item separator = { " " | "\t" | "\n" | ";" | "" } ;

.. code-block:: javascript

    "one line" { "name":i = 0; "name":i = 1}
                             ^^            ^^
                                           <empty>
    "multi line" {
        "name":i = 0
                    ^
        "name":i = 1
                    ^
    }
     ^
    name:i = 0// null
              ^
              <empty>

Место разделителя элементов секции

.. code-block:: text

     item
    ^    ^

Разделители элементов вектора
=============================

.. code-block:: text

    optional value separator = { " " | "\t" | "" } ;
    vector element separator = optional value separator , ",", optional value separator ;

.. code-block:: javascript

    point2d:ip2 = 1, 2
                   ^^

Место разделителя элементов вектора

.. code-block:: text

    point:tag = element0, element1
                        ^^

Разделители внутри параметров и секций
======================================

.. code-block:: text

    optional whitespace = { " " | "\t" | "\n" | "" } ;
    name tag separator = optional whitespace, ":", optional whitespace ;
    tag value separator = optional whitespace, "=", optional whitespace ;
    name value separator = optional whitespace ;
    section begin = optional whitespace, "{", optional item separator ;
    section end = optional item separator, "}" ;

.. code-block:: javascript

    m:i = 1
     ^ ^^^
    group
         ^
    {
    ^^
        n:i = 2
         ^ ^^^
        n:i = 3
         ^ ^^^
    }
    ^

Место разделителей

.. code-block::

    parameter : t = value
             ^^^ ^^^
    section { items }
           ^^^     ^^
