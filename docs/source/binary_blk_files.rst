==================
Двоичные файлы BLK
==================

-------------
Файл типа FAT
-------------

Автономный файл.

Примеры:

* ``WarThunder/game.vromfs.bin/danetlibs/route_prober/templates/route_prober.blk``
* ``tests/samples/section_fat.blk``

.. drawio-image:: diagrams/section_fat.drawio

BlkType.FAT
    Byte, тип файла 1.

Names container
    Контейнер имен.

Blocks container
    Контейнер блоков.

Диаграмма для ``tests/samples/section_fat.blk``

.. drawio-image:: diagrams/section_fat_dump.drawio

-----------------
Файл типа FAT_ZST
-----------------

Автономный файл со сжатым zstd контейнером.

--------------
Файл типа SLIM
--------------

Неавтономный файл, разделяющий последовательность имен.

------------------
Файл типа SLIM_ZST
------------------

Неавтономный файл, разделяющий последовательность имен со сжатым zstd контейнером.

-----------------------
Файл типа SLIM_ZST_DICT
-----------------------

Неавтономный файл, разделяющий последовательность имен со сжатым zstd контейнером, с использованием словаря.

-------------
Файл типа BBF
-------------

Автономный файл старого формата.

------------------
Файл типа BBF_ZLIB
------------------

Автономный файл старого формата со сжатым zlib контейнером.

-------
Файл NM
-------

Файл разделяемой последовательности имен.

Примеры:

* ``WarThunder/gui.vromfs.bin/nm``
* ``tests/samples/nm``

.. drawio-image:: diagrams/nm.drawio

Table digest
    64-битный идентификатор таблицы. Алгоритм построения неизвестен.

Dict digest
    256-битный идентификатор таблицы. Алгоритм построения неизвестен.

Compressed names container
    Контейнер имен, сжатый по алгоритму zstandard без использования словаря.

Диаграмма для ``tests/samples/nm``

.. drawio-image:: diagrams/nm_dump.drawio


Контейнер имен
==============

Блок контейнера имен.

.. drawio-image:: diagrams/names_container.drawio

Names count
    VarInt, число строк в последовательности.

Names array size
    VarInt, размер массива строк

Names array
    Массив C-строк.

Диаграмма для ``tests/samples/names_container``

.. drawio-image:: diagrams/names_container_dump.drawio

.. list-table:: Карта имен
    :header-rows: 1
    :align: left

    * - Индекс
      - Имя | Строка
    * - 0
      - ``'vec4f'``
    * - 1
      - ``'int'``
    * - 2
      - ``'long'``
    * - 3
      - ``'alpha'``
    * - 4
      - ``'str'``
    * - 5
      - ``'bool'``
    * - 6
      - ``'color'``
    * - 7
      - ``'gamma'``
    * - 8
      - ``'vec2i'``
    * - 9
      - ``'vec2f'``
    * - a
      - ``'transform'``
    * - b
      - ``'beta'``
    * - c
      - ``'float'``
    * - d
      - ``'vec3f'``
    * - e
      - ``'hello'``



