# Documentation for BLK Files

## Runtime

Linux, Python 3.7 for PyPy3 compatibility.

## Installation

```pip install .```

## Building Documentation

Diagrams built using [drawio](https://github.com/jgraph/drawio-desktop/)

Available languages : 
- Russian : "ru"
- English : "en"

```
pip install -r requirements-docs.txt
set SPHINXOPTS=-D language=[language]
docs\make.bat html
```