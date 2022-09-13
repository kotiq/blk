__all__ = [
    'ConstructError',
    'ComposeError',
    'SerializeError'
]


class ConstructError(Exception):
    pass


class ComposeError(ConstructError):
    pass


class SerializeError(ConstructError):
    pass
