__all__ = [
    'DirectoryError',
    'DirectoryUnpackError',
    'NameUnpackError',
    'DictUnpackError',
    'FileUnpackError',
]


class DirectoryError(Exception):
    pass


class DirectoryUnpackError(DirectoryError):
    pass


class NameUnpackError(DirectoryUnpackError):
    pass


class DictUnpackError(DirectoryUnpackError):
    pass


class FileUnpackError(DirectoryUnpackError):
    pass
