# Documentation for BLK Files

<p align="left">
  <span>English</span> |
  <a href="https://github.com/kotiq/blk/tree/docs/lang/russian#вспомогательный-инcтрументарий-для-работы-с-файлами-конфигурации">Русский</a>
</p>

## Runtime

Linux, Python 3.7 for PyPy3 compatibility.

## Installation

```pip install .```

## Building Documentation

Diagrams built using [drawio](https://github.com/jgraph/drawio-desktop/)

Available languages : 
- English : "en"
- Russian : "ru"

```
pip install -r requirements-docs.txt
set SPHINXOPTS=-D language=[language]
docs\make.bat html
```