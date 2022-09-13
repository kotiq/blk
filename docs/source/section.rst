Инструкции
==========

Включение секции из файла
-------------------------

Используется для сборки секции из нескольких файлов.
После исполнения в место именованного параметра включается секция из текстового blk файла, на который указывает путь.

Построение секции из пары файлов
""""""""""""""""""""""""""""""""

Пусть имеется структура директорий:

.. code-block:: text

    .
    ├── common
    │   └── metadata.blk
    └── config_tpl.blk

Содержимое ``config_tpl.blk``

.. code-block:: javascript

    // config_tpl.blk

    include "common/metadata.blk"

    "debug" {
      "enableNvHighlights":t = "auto"
      "screenshotAsJpeg":b = yes
      "512mboughttobeenoughforanybody":b = no
      "netLogerr":b = yes
    }

Содержимое ``common/metadata.blk``

.. code-block:: javascript

    // common/metadata.blk

    "author":t = "kotiq"
    "version":i = 16909060

Представление ``config_tpl.blk`` в виде секции до обработки.

.. code-block:: javascript

    "@commentCPP":t = "config_tpl.blk"
    "@include":t = "common/metadata.blk"
    "debug" {
      "enableNvHighlights":t = "auto"
      "screenshotAsJpeg":b = yes
      "512mboughttobeenoughforanybody":b = no
      "netLogerr":b = yes
    }


Представление ``common/metadata.blk`` в виде секции до обработки.

.. code-block:: javascript

    "@commentCPP":t = "common/metadata.blk"
    "author":t = "kotiq"
    "version":i = 16909060

Представление ``config_tpl.blk`` в виде секции после удаления комментариев.

.. code-block:: javascript

    "@include":t = "common/metadata.blk"
    "debug" {
      "enableNvHighlights":t = "auto"
      "screenshotAsJpeg":b = yes
      "512mboughttobeenoughforanybody":b = no
      "netLogerr":b = yes
    }


Представление ``common/metadata.blk`` в виде секции после удаления комментариев.

.. code-block:: javascript

    "author":t = "kotiq"
    "version":i = 16909060

Результирующая секция после включения секции из файла.

.. code-block:: javascript

    "author":t = "kotiq"
    "version":i = 16909060
    "debug" {
      "enableNvHighlights":t = "auto"
      "screenshotAsJpeg":b = yes
      "512mboughttobeenoughforanybody":b = no
      "netLogerr":b = yes
    }


