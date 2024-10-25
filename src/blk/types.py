from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import (List, NamedTuple, Optional, Sequence, Tuple, cast)
from ctypes import c_float
from collections import OrderedDict, deque
from math import isfinite, isclose

__all__ = [
    'BlockComment',
    'Bool',
    'Color',
    'Command',
    'Comment',
    'CycleError',
    'DictSection',
    'EncodedStr',
    'Float',
    'Float12',
    'Float2',
    'Float3',
    'Float4',
    'Include',
    'IncludeError',
    'Int',
    'Int2',
    'Int3',
    'Item',
    'LineComment',
    'ListSection',
    'LoadFileError',
    'Long',
    'MultiValueError',
    'Name',
    'NoCDKPathError',
    'NoRootPathError',
    'Parameter',
    'Section',
    'SectionError',
    'Size',
    'Str',
    'UByte',
    'Value',
    'Var',
    'Vector',
    'false',
    'true'
]


class SectionError(Exception):
    """Ошибка секции."""


class CycleError(SectionError):
    """Секция содержит цикл."""


class MultiValueError(SectionError):
    """Ошибка структуры секции."""

    def __init__(self, fst_type, type_):
        self.fst_type = fst_type
        self.type = type_
        super().__init__('Ожидалось {fst_type}: {type}'.format(fst_type=fst_type, type=type_))


class IncludeError(SectionError):
    """Ошибка при вставке содержимого секции."""


class NoCDKPathError(IncludeError):
    """Отсутствует путь к CDK."""

    def __init__(self, path):
        self.path = path
        super().__init__('Не задан путь CDK для {path}'.format(path=path))


class NoRootPathError(IncludeError):
    """Отсутствует путь к корневой директории ресурсов."""

    def __init__(self, path):
        self.path = path
        super().__init__('Не задан путь директории ресурсов для {path}'.format(path=path))


class LoadFileError(IncludeError):
    """Ошибка загрузки секции из файла."""

    def __init__(self, path, working_path, cdk_path, root_path):
        self.path = path
        self.working_path = working_path
        self.cdk_path = cdk_path
        self.root_path = root_path
        super().__init__('Ошибка при загрузке секции для {path}, w={working_path}, c={cdk_path}, r={root_path}'
                         .format(**vars(self)))


class Var:
    """Простая обертка значения."""

    __slots__ = ('value',)

    def __init__(self, init):
        self.value = init

    def __repr__(self):
        return f'{self.__class__.__name__}({self.value!r})'


class Value:
    """Общий класс значений."""


class Parameter(Value):
    """Общий класс параметров."""


class Scalar(Parameter):
    """Общий класс скалярных параметров."""


class Bool(int, Scalar):
    """Булево значение."""

    def __repr__(self):
        return 'true' if self else 'false'


true = Bool(1)
"""Истина."""

false = Bool(0)
"""Ложь."""


class EncodedStr(str):
    """Общий класс имен и строк UTF-8."""

    encodings = ('utf8', 'cp1251')

    @classmethod
    def of(cls, xs):
        if isinstance(xs, bytes):
            for e in cls.encodings:
                try:
                    return cls(xs.decode(e))
                except UnicodeDecodeError:
                    continue
            raise ValueError('Не удалось декодировать как {} последовательность: {}'
                             .format('|'.join(cls.encodings), xs))
        elif isinstance(xs, str):
            return cls(xs)
        else:
            raise TypeError('xs: ожидалось AnyStr: {}'.format(type(xs)))


class Str(EncodedStr, Scalar):
    """Строка UTF-8."""

    def __repr__(self):
        return f'{self.__class__.__name__}({str.__repr__(self)})'


SafeStr = Str.of
"""Безопасная Фабрика строк UTF-8."""


class Integer(int, Scalar):
    signed = ...
    max_bit_length = ...
    min = ...
    max = ...

    @classmethod
    def of(cls, x):
        return cls(cls.validated(x))

    @classmethod
    def validated(cls, x):
        if not isinstance(x, int):
            raise TypeError('x: ожидалось int: {}'.format(type(x)))

        if not cls.min <= x <= cls.max:
            raise ValueError('x: ожидалось Int{}{}: {:#_x}'.format(cls.max_bit_length, 's' if cls.signed else '', x))

        return x


def ranged(cls):
    if not (hasattr(cls, 'min') and isinstance(cls.min, int)):
        cls.min = -2 ** (cls.max_bit_length - 1) if cls.signed else 0

    if not (hasattr(cls, 'max') and isinstance(cls.max, int)):
        cls.max = 2 ** (cls.max_bit_length - 1) - 1 if cls.signed else 2 ** cls.max_bit_length - 1

    return cls


@ranged
class Int(Integer):
    """Целое."""

    signed = True
    max_bit_length = 32
    fmt = ''

    def __repr__(self):
        return f'{self.__class__.__name__}({int.__repr__(self)})'


SafeInt = Int.of
"""Безопасная фабрика целых."""


@ranged
class UByte(Integer):
    """Беззнаковое целое 8 бит."""

    signed = False
    max_bit_length = 8
    fmt = '#x'

    def __repr__(self):
        return f'{self.__class__.__name__}({int.__repr__(self)})'


SafeUByte = UByte.of
"""Безопасная фабрика беззнаковых целых 8 бит."""


@ranged
class Long(Integer):
    """Длинное целое."""

    signed = True
    max_bit_length = 64
    fmt = ''

    def __repr__(self):
        return f'{self.__class__.__name__}({int.__repr__(self)})'


SafeLong = Long.of
"""Безопасная фабрика длинных целых."""


class Float(float, Scalar):
    """Рациональное."""

    rel_tol = 1e-05
    abs_tol = 1e-08
    fmt = '.7g'

    def __repr__(self):
        return f'{self.__class__.__name__}({float.__format__(self, self.fmt)})'

    @classmethod
    def of(cls, x):
        return cls(cls.validated(x))

    @classmethod
    def validated(cls, x):
        if not isinstance(x, (float, int)):
            raise TypeError('x: ожидалось float | int: {}'.format(type(x)))
        y = c_float(x).value
        if not isfinite(y):
            raise ValueError('x: разрешены только конечные числа')
        return y

    def close_to(self, other):
        return isclose(self, other, rel_tol=Float.rel_tol, abs_tol=Float.abs_tol)


SafeFloat = Float.of
"""Безопасная фабрика рациональных."""


class Vector(Tuple, Parameter, metaclass=ABCMeta):
    type = ...
    size = ...

    def __repr__(self):
        fmt = self.type.fmt
        return f'{self.__class__.__name__}(({", ".join(map(lambda x: format(x, fmt), self))}))'

    @classmethod
    def of(cls, xs):
        if not isinstance(xs, Sequence):
            raise TypeError('Ожидалась последовательность: {}'.format(type(xs)))
        sz = len(xs)
        if sz != cls.size:
            raise TypeError('Ожидалось {} компонент: {}'.format(cls.size, sz))
        return cls(map(cls.type.validated, xs))

    def close_to(self, other):
        return len(self) == len(other) and all(Float.close_to(x, y) for x, y in zip(self, other))


class Int2(Vector):
    """Вектор целых 1х2."""

    type = Int
    size = 2


SafeInt2 = Int2.of
"""Безопасная фабрика векторов целых 1х2."""


class Int3(Vector):
    """Вектор целых 1x3."""

    type = Int
    size = 3


SafeInt3 = Int3.of
"""Безопасная фабрика векторов целых 1x3."""


class Color(Vector):
    """Цвет."""

    type = UByte
    size = 4


SafeColor = Color.of
"""Безопасная фабрика цвета."""


class Float2(Vector):
    """Вектор рациональных 1x2."""

    type = Float
    size = 2


SafeFloat2 = Float2.of
"""Безопасная фабрика векторов рациональных 1x2."""


class Float3(Vector):
    """Вектор рациональных 1x3."""

    type = Float
    size = 3


SafeFloat3 = Float3.of
"""Безопасная фабрика векторов рациональных 1x3."""


class Float4(Vector):
    """Вектор рациональных 1x4."""

    type = Float
    size = 4


SafeFloat4 = Float4.of
"""Безопасная фабрика векторов рациональных 1x4."""


class Float12(Vector):
    """Вектор рациональных 1x12."""

    type = Float
    size = 12


SafeFloat12 = Float12.of
"""Безопасная фабрика векторов рациональных 1x12."""


class Name(EncodedStr):
    """Имя."""

    of_root = None

    def __repr__(self):
        return f'{self.__class__.__name__}({str.__repr__(self)})'


SafeName = Name.of


class Size(NamedTuple):
    params_count: int
    blocks_count: int


# todo: удалить Item
Item = Tuple[Name, Value]
_default = object()


class add:
    @staticmethod
    def _make_inst_getter_name(cls):
        return f'get_{cls.__name__.lower()}'

    @staticmethod
    def _make_first_inst_getter_name(cls):
        return f'get_first_{cls.__name__.lower()}'

    @staticmethod
    def _make_all_insts__abc_getter_name(cls):
        return f'get_all_{cls.__name__.lower()}s'

    @staticmethod
    def _make_all_insts_getter_name(cls):
        name = cls.__name__.lower()
        type_name = 'section' if name in ('listsection', 'dictsection') else name
        return f'get_all_{type_name}s'

    _make_all_insts__dict_getter_name = _make_all_insts__list_getter_name = _make_all_insts_getter_name

    @staticmethod
    def _make_inst_getter(cls):
        def get_inst(self, name: str, index=0, default=None):
            value = self.get(name, index)
            return default if value is None or not isinstance(value, cls) else value

        return get_inst

    @staticmethod
    def _make_first_inst_getter(cls):
        def get_first_inst(self, name, default=None):
            inst_getter = getattr(self, add._make_inst_getter_name(cls))
            return inst_getter(name, 0, default)

        return get_first_inst

    @staticmethod
    def _make_all_insts__abc_getter(cls):
        @abstractmethod
        def get_all_insts(self, name, default=_default):
            raise NotImplementedError

        return get_all_insts

    @staticmethod
    def _make_all_insts__dict_getter(cls):
        def get_all_insts(self, name, default=_default):
            values = self.get_all(name)
            if values and isinstance(values[0], cls):
                return values

            return [] if default is _default else default

        return get_all_insts

    @staticmethod
    def _make_all_insts__list_getter(cls):
        def get_all_insts(self, name, default=_default):
            values = []
            i = 0
            for n, v in self:
                if n == name:
                    if i == 0 and not isinstance(v, cls):
                        break
                    values.append(v)
                    i += 1

            if values:
                return values

            return [] if default is _default else default

        return get_all_insts

    @staticmethod
    def getters(cls):
        if cls.__name__ == 'DictSection':
            ids = ('all_insts__dict',)
        elif cls.__name__ == 'ListSection':
            ids = ('all_insts__list',)
        elif cls.__name__ == 'Section':
            ids = ('inst', 'first_inst', 'all_insts__abc',)
        else:
            raise NotImplementedError

        return add._getters(cls, ids)

    @staticmethod
    def _getters(cls, ids):
        for kls in (cls, Str, Int, Float, Float2, Float3, Float4,
                    Int2, Int3, Bool, Color, Float12, Long):
            for id_ in ids:
                name_builder = getattr(add, f'_make_{id_}_getter_name')
                getter_name = name_builder(kls)
                getter_builder = getattr(add, f'_make_{id_}_getter')
                getter = getter_builder(kls)
                getter.__name__ = getter_name
                setattr(cls, getter_name, getter)

        return cls


@add.getters
class Section(Value, metaclass=ABCMeta):
    @classmethod
    def of(cls, section):
        """Строит копию секции с типом получателя.

        Секции не содержат команд.
        """

        root = cls()
        for name, value in section.pairs():
            if isinstance(value, Section):
                value = cls.of(value)  # @r
            root.append((name, value))
        return root

    @abstractmethod
    def append(self, item):
        """Небезопасное добавление пары в секцию.

        :param item: Пара, добавляемая в секцию.
        """

        raise NotImplementedError

    @abstractmethod
    def add(self, name, value):
        """Безопасное добавление пары в секцию.

        :param name: Имя формируемой пары.
        :param value: Значение формируемой пары.
        :raise TypeError: Имя не является строкой или значение не является Value.
        :raise MultiValueError: Типы значений в мультизначении различны.
        """

        raise NotImplementedError

    @abstractmethod
    def get(self, name, index=0, default=None):
        """Значение в мультизначении по имени и индексу или значение по умолчанию.

        :param name: Имя пары.
        :param index: Номер пары, начиная с 0.
        :param default: Значение по умолчанию.
        """

        raise NotImplementedError

    def get_first(self, name, default=None):
        return self.get(name, 0, default)

    @abstractmethod
    def get_all(self, name, default=_default):
        """Список всех значений в имультизначении по имени или значение по умолчанию.

        :param name: Имя всех пар.
        :param default: Значение по умолчанию.
        :return: Все значения по имени.
        """

        raise NotImplementedError

    def add_str(self, name, value):
        """Добавить именованную строку.

        :param name: Имя
        :param value: Строка
        """

        self.add(name, Str.of(value))

    def add_int(self, name, value):
        """Добавить именованное целое.

        :param name: Имя
        :param value: Целое, Int32s
        """

        self.add(name, Int.of(value))

    def add_float(self, name, value):
        """Добавить именованное рациональное.

        :param name: Имя
        :param value: Рациональное, Float32
        """

        self.add(name, Float.of(value))

    def add_float2(self, name, x, y):
        """Добавить именованный вектор рациональных 1x2.

        :param name: Имя
        :param x: Первое рациональное, Float32
        :param y: Второе рациональное, Float32
        """

        xs = (x, y)
        self.add(name, Float2.of(xs))

    def add_float3(self, name, x, y, z) -> None:
        """Добавить именованный вектор рациональных 1x3.

        :param name: Имя
        :param x: Первое рациональное, Float32
        :param y: Второе рациональное, Float32
        :param z: Третье рациональное, Float32
        """

        xs = (x, y, z)
        self.add(name, Float3.of(xs))

    def add_float4(self, name, x, y, z, w) -> None:
        """Добавить именованный вектор рациональных 1x4.

        :param name: Имя
        :param x: Первое рациональное, Float32
        :param y: Второе рациональное, Float32
        :param z: Третье рациональное, Float32
        :param w: Четвертое рациональное, Float32
        """

        xs = (x, y, z, w)
        self.add(name, Float4.of(xs))

    def add_int2(self, name, x, y) -> None:
        """Добавить именованный вектор целых 1x2.

        :param name: Имя
        :param x: Первое целое, Int32s
        :param y: Второе целое, Int32s
        """

        xs = (x, y)
        self.add(name, Int2.of(xs))

    def add_int3(self, name, x, y, z) -> None:
        """Добавить именованный вектор целых 1x3.

        :param name: Имя
        :param x: Первое целое, Int32s
        :param y: Второе целое, Int32s
        :param z: Третье целое, Int32s
        """

        xs = (x, y, z)
        self.add(name, Int3.of(xs))

    def add_bool(self, name, value) -> None:
        """Добавить именованное булево.

        :param name: Имя
        :param value: Булево
        """

        self.add(name, Bool(value))

    def add_false(self, name):
        """Добавить именованное ``Ложь``.

        :param name: Имя
        """

        self.add_bool(name, False)

    def add_true(self, name):
        """Добавить именованное ``Истина``.

        :param name: Имя
        """

        self.add_bool(name, True)

    def add_color(self, name, r, g, b, a=255):
        """Добавить именованный цвет.

        :param name: Имя
        :param r: Красный, Int8u
        :param g: Зеленый, Int8u
        :param b: Синий, Int8u
        :param a: Прозрачность, Int8u
        """

        xs = (r, g, b, a)
        self.add(name, Color.of(xs))

    def add_float12(self, name,
                    rx, ry, rz,
                    ux, uy, uz,
                    fx, fy, fz,
                    px, py, pz,
                    ):
        """Добавить именованный вектор рациональных 4x3.

        :param name: Имя
        :param rx: Право, первая компонента, Float32
        :param ry: Право, вторая компонента, Float32
        :param rz: Право, третья компонента, Float32
        :param ux: Верх, первая компонента, Float32
        :param uy: Верх, вторая компонента, Float32
        :param uz: Верх, третья компонента, Float32
        :param fx: Перед, первая компонента, Float32
        :param fy: Перед, вторая компонента, Float32
        :param fz: Перед, третья компонента, Float32
        :param px: Начало, первая компонента, Float32
        :param py: Начало, вторая компонента, Float32
        :param pz: Начало, третья компонента, Float32
        """

        xs = (rx, ry, rz, ux, uy, uz, fx, fy, fz, px, py, pz)
        self.add(name, Float12.of(xs))

    def add_long(self, name, value):
        """Добавить именованное длинное целое.

        :param name: Имя
        :param value: Длинное целое, Int64s
        """

        self.add(name, Long.of(value))


    @abstractmethod
    def pairs(self):
        """
        :return: Итератор пар в секции.
        """

        raise NotImplementedError

    @abstractmethod
    def check_cycle(self):
        """
        :raise CycleError: Секция содержит цикл.
        """

        raise NotImplementedError


# todo: ограничить уровень вложенности секций до 512
# todo: для безопасного добавления пары в случае секции проверить на цикл


@add.getters
class DictSection(OrderedDict, Section):
    def append(self, item):
        name, value = item
        if name not in self:
            self[name] = []

        self[name].append(value)

    def add(self, name, value):
        if not isinstance(name, EncodedStr):
            name = Name.of(name)
        elif isinstance(name, Str):
            name = Name(name)

        if not isinstance(value, Value):
            raise TypeError('value: ожидалось Value: {}'.format(type(value)))

        values = cast(Optional[List[Value]], super().get(name))
        if values:
            fst_type = type(values[0])
            type_ = type(value)
            if fst_type is not type_:
                raise MultiValueError(fst_type, type_)

        self.append((name, value))

    def get(self, name, index=0, default=None):
        try:
            return self[name][index]
        except (KeyError, IndexError):
            return default

    def get_all(self, name, default=_default):
        try:
            return list(self[name])
        except KeyError:
            return [] if default is _default else default

    def get_all_sections(self, name, default = ...):
        raise NotImplementedError

    def get_all_strs(self, name, default = ...):
        raise NotImplementedError

    def get_all_ints(self, name, default = ...):
        raise NotImplementedError

    def get_all_floats(self, name, default = ...):
        raise NotImplementedError

    def get_all_float2s(self, name, default = ...):
        raise NotImplementedError

    def get_all_float3s(self, name, default = ...):
        raise NotImplementedError

    def get_all_float4s(self, name, default = ...):
        raise NotImplementedError

    def get_all_int2s(self, name, default = ...):
        raise NotImplementedError

    def get_all_int3s(self, name, default = ...):
        raise NotImplementedError

    def get_all_bools(self, name, default = ...):
        raise NotImplementedError

    def get_all_colors(self, name, default = ...):
        raise NotImplementedError

    def get_all_float12s(self, name, default = ...):
        raise NotImplementedError

    def get_all_longs(self, name, default = ...):
        raise NotImplementedError

    def pairs(self):
        """Пары в порядке добавления первого имени.

        :return: Итератор пар в секции.
        """

        for name, values in self.items():
            if len(values) == 1:
                yield name, values[0]
            else:
                for value in values:
                    yield name, value

    def sorted_pairs(self):
        """Пары в порядке появления в двоичном файле.

        Сначала все параметры на уровне затем все секции на уровне, в порядке добавления первого имени."""

        sections_pairs = []
        for item in self.pairs():
            value = item[1]
            if isinstance(value, Section):
                sections_pairs.append(item)
            elif isinstance(value, Parameter):
                yield item

        yield from sections_pairs

    def _bfs_pairs_gen(self, pairs_of):
        """Генератор пар при обходе секции в ширину с параметром.

        :param pairs_of: Генератор потомков на уровне
        :return: Генератор пар при обходе секции в ширину
        """

        queue = deque()
        queue.append((Name.of_root, self))

        while queue:
            item = queue.popleft()
            yield item
            value = item[1]
            if isinstance(value, Section):
                for item in pairs_of(value):
                    queue.append(item)

    def bfs_sorted_pairs(self):
        """Генератор пар при обходе секции в ширину."""

        yield from self._bfs_pairs_gen(lambda s: s.sorted_pairs())

    def _names_dfs_nlr_rec(self):
        """Генератор имен при обходе секции в глубину, рекурсивная версия."""

        for name, values in self.items():
            yield name
            for value in values:
                if isinstance(value, DictSection):
                    yield from DictSection._names_dfs_nlr_rec(value)  # @r

    names = _names_dfs_nlr_rec

    def _strings_dfs_nlr_rec(self):
        """Генератор строк при обходе секции в глубину, рекурсивная версия."""

        for name, values in self.items():
            for value in values:
                if isinstance(value, DictSection):
                    yield from DictSection._strings_dfs_nlr_rec(value)  # @r
                elif isinstance(value, Str):
                    yield value

    strings = _strings_dfs_nlr_rec

    def size(self):
        """Размер секции на уровне.

        :return: (число параметров, число секций)
        """

        params_count, sections_count = 0, 0
        for name, value in self.pairs():
            if isinstance(value, Parameter):
                params_count += 1
            elif isinstance(value, Section):
                sections_count += 1

        return Size(params_count, sections_count)  # noqa

    def check_cycle(self):
        """
        Проверка секции на цикл.

        :raise CycleError: Найден цикл
        """

        def g(section: DictSection, ids):
            """
            :param section: Проверяемая секция
            :param ids: id верхних уровней
            :raise CycleError: Найден цикл
            """

            for name, value in section.pairs():
                if isinstance(value, DictSection):
                    id_ = id(value)
                    if id_ in ids:
                        raise CycleError
                    else:
                        ids.add(id_)
                        g(value, ids)
                        ids.remove(id_)

        g(self, {id(self)})

    def __repr__(self):
        return f'{self.__class__.__name__}([{", ".join(map(repr, self.items()))}])'


class Command(tuple):
    prefix = '@'
    sep = ':'
    name = ...


class Comment(Command):
    prefix = Command.prefix + 'comment'

    def __new__(cls, value):
        value = Str(value)
        return super().__new__(cls, (cls.name, value))

    @property
    def text(self):
        return self[1]

    @classmethod
    def _check(cls, text):
        raise NotImplementedError

    @classmethod
    def of(cls, text):
        cls._check(text)
        return cls(text)

    def __repr__(self):
        return f'{self.__class__.__name__}({str.__repr__(self[1])})'


class LineComment(Comment):
    """
    Строчный комментарий C++.

    // text
    """

    name = Name(Comment.prefix + 'CPP')

    @classmethod
    def _check(cls, text):
        if '\n' in text or '\r' in text:
            raise ValueError('Строчный комментарий содержит перенос строки: {!r}'.format(text))


SafeLineComment = LineComment.of


class BlockComment(Comment):
    """
    Блочный комментарий C.

    | /*
    | text
    | */
    """

    name = Name(Comment.prefix + 'C')

    @classmethod
    def _check(cls, text):
        if '*/' in text:
            raise ValueError('Блочный комментарий содержит конец комментария: {!r}'.format(text))


SafeBlockComment = BlockComment.of


class Modifier(Command):
    ...


class Include(Command):
    """
    Вставка секции.

    include text
    """

    name = Name(Command.prefix + 'include')
    cdk_prefix = '#'
    root_prefix = ':'

    def __new__(cls, value):
        if not value:
            raise ValueError("Пустой путь.")
        if not isinstance(value, Str):
            value = Str(value)
        return super().__new__(cls, (cls.name, value))

    @property
    def path(self):
        return Path(self[1])

    def __repr__(self):
        return f'{self.__class__.__name__}({str.__repr__(self[1])})'


# todo: использовать связанный список, а не динамический массив
@add.getters
class ListSection(list, Section):
    """Представление текста без учета разделителей пар. Пары с сохранением порядка."""

    def add(self, name, value):
        if not isinstance(name, EncodedStr):
            name = Name.of(name)
        elif isinstance(name, Str):
            name = Name(name)

        if not isinstance(value, Value):
            raise TypeError('value: ожидалось Value: {}'.format(type(value)))

        for n, v in self:
            if n == name:
                fst_type = type(v)
                type_ = type(value)
                if fst_type is not type_:
                    raise MultiValueError(fst_type, type_)
                break

        self.append((name, value))

    def add_comment(self, text):
        ctor = BlockComment if ('\n' in text or '\r' in text) else LineComment
        comment = ctor(text)
        self.append(comment)  # noqa

    def add_include(self, path):
        include = Include(path)
        self.append(include)  # noqa

    def pairs(self):
        return iter(self)

    def get_index(self, p):
        """Индекс первой пары, для которой выполняется предикат p.

        :return: Индекс или ``None``
        """

        for i, item in enumerate(self):
            if p(item):
                return i
        return None

    def get_indices(self, p):
        """Индексы пар, удовлетворяющих предикату p."""

        return [i for i, item in enumerate(self) if p(item)]

    def get_item(self, p):
        """Первая пара, удовлетворяющая предикату p."""

        for item in self:
            if p(item):
                return item
        return None

    def get_items(self, p):
        """Пары, удовлетворяющие предикату p."""

        return list(filter(p, self))

    def set_item(self, p, item):
        """Замена первой пары, удовлетворяющей предикату p."""

        i = self.get_index(p)
        if i is not None:
            super().__setitem__(i, item)

    def get(self, name, index=0, default=None):
        i = 0
        for n, v in self:
            if n == name:
                if i == index:
                    return v
                i += 1

        return default

    def get_all(self, name, default=_default):
        values = [v for n, v in self if n == name]
        if values:
            return values

        return [] if default is _default else default

    def get_all_sections(self, name, default = ...):
        raise NotImplementedError

    def get_all_strs(self, name, default = ...):
        raise NotImplementedError

    def get_all_ints(self, name, default = ...):
        raise NotImplementedError

    def get_all_floats(self, name, default = ...):
        raise NotImplementedError

    def get_all_float2s(self, name, default = ...):
        raise NotImplementedError

    def get_all_float3s(self, name, default = ...):
        raise NotImplementedError

    def get_all_float4s(self, name, default = ...):
        raise NotImplementedError

    def get_all_int2s(self, name, default = ...):
        raise NotImplementedError

    def get_all_int3s(self, name, default = ...):
        raise NotImplementedError

    def get_all_bools(self, name, default = ...):
        raise NotImplementedError

    def get_all_colors(self, name, default = ...):
        raise NotImplementedError

    def get_all_float12s(self, name, default = ...):
        raise NotImplementedError

    def get_all_longs(self, name, default = ...):
        raise NotImplementedError

    def remove_comments(self):
        """Удалить комментарии из дерева."""

        indices = []
        for i, (n, v) in enumerate(self.pairs()):
            if n in (LineComment.name, BlockComment.name):
                indices.append(i)
            elif isinstance(v, ListSection):
                v.remove_comments()  # @r

        for i in reversed(indices):
            del self[i]

    def include_files(self, working_path=Path.cwd(), cdk_path=None, root_path=None):
        """Вставка содержимого подсекций из файлов.

        :raise IncludeError: ``cdk_path`` или ``root_path`` требуются, но не заданы. Ошибка при загрузке секции из файла.
        """

        indices = []
        for i, (n, v) in enumerate(self.pairs()):
            if n == Include.name:
                if not isinstance(v, Str):
                    raise SectionError('Пара {} не является командой включения: {!r}, {!r}'.format(i, n, v))
                indices.append(i)
            elif isinstance(v, ListSection):
                v.include_files(working_path, cdk_path, root_path)  # @r

        if not indices:
            return

        for i in reversed(indices):
            path = Include.path.fget(self[i])
            fst_part = path.parts[0]

            if fst_part == Include.cdk_prefix:
                if cdk_path is None:
                    raise NoCDKPathError(path)
                prefix = cdk_path
            elif fst_part == Include.root_prefix:
                if root_path is None:
                    raise NoRootPathError(path)
                prefix = root_path
            else:
                prefix = working_path

            file_path = prefix / path
            try:
                section = compose_file(file_path, False, True, cdk_path, root_path)
            except (OSError, ComposeError) as e:
                raise LoadFileError(path, working_path, cdk_path, root_path) from e
            else:
                del self[i]
                for j, p in enumerate(section.pairs()):
                    self.insert(i + j, p)

    def __call__(self):
        """Выполнение команд, удаление комментариев."""

        raise NotImplementedError

    def check_cycle(self) -> None:
        raise NotImplementedError


from blk.text.error import ComposeError
from blk.text.composer import compose_file
