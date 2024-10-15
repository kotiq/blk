from os import PathLike
from pathlib import Path
from typing import Callable, TextIO, Union
from _pytest.tmpdir import TempPathFactory

def make_outpath(name: str) -> Callable[[Path], Path]: ...

def make_tmppath(str) -> Callable[[TempPathFactory], Path]: ...

def create_text(path: Union[str, PathLike[str]]) -> TextIO: ...
