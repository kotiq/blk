__all__ = [
    'ConstructError',
    'ComposeError',
    'SerializeError'
]


class ConstructError(Exception):
    pass


class ComposeError(ConstructError):
    def __init__(self):
        super().__init__('Ошибка при сборке секции из потока.')


class SerializeError(ConstructError):
    pass
