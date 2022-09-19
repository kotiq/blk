import abc
from pathlib import Path
from typing import (Any, Callable, ClassVar, Iterable, NamedTuple, Optional, Sequence, Set, Tuple, Type, TypeVar, Union,
                    overload)
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
    'Float2',
    'Float3',
    'Float3',
    'Float4',
    'Float4',
    'Include',
    'Int',
    'Int2',
    'Int3',
    'Item',
    'LineComment',
    'ListSection',
    'Long',
    'Name',
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
    'method',
    'true'
]


class SectionError(Exception):
    """Ошибка структуры секции."""


class CycleError(SectionError):
    """Секция содержит цикл."""


class Var:
    __slots__ = ('value',)

    def __init__(self, init) -> None:
        self.value = init

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.value!r})'


def method(cls: type) -> Callable[[Callable], Callable]:
    def decorator(f: Callable) -> Callable:
        setattr(cls, f.__name__, f)
        return f

    return decorator


class Value:
    pass


class Parameter(Value):
    pass


class Scalar(Parameter):
    pass


class Bool(int, Scalar):
    def __repr__(self) -> str:
        return 'true' if self else 'false'


true = Bool(1)
false = Bool(0)


class EncodedStr(str):
    encodings = ('utf8', 'cp1251')

    @classmethod
    @overload
    def of(cls, xs: bytes) -> 'EncodedStr':
        ...

    @classmethod
    @overload
    def of(cls, xs: str) -> 'EncodedStr':
        ...

    @classmethod
    @overload
    def of(cls, xs: bytes, encodings: Tuple[str, ...]) -> 'EncodedStr':
        ...

    @classmethod
    @overload
    def of(cls, xs: str, encodings: Tuple[str, ...]) -> 'EncodedStr':
        ...

    @classmethod
    def of(cls, xs: Union[bytes, str], encodings: Optional[Tuple[str, ...]] = None) -> 'EncodedStr':
        if isinstance(xs, bytes):
            if isinstance(encodings, str):
                try:
                    return cls(xs.decode(encodings))
                except UnicodeDecodeError:
                    raise ValueError('Не удалось декодировать как {} последовательность: {}'.format(encodings, xs))
            else:
                if encodings is None:
                    encodings = cls.encodings
                for e in encodings:
                    try:
                        return cls(xs.decode(e))
                    except UnicodeDecodeError:
                        continue
                raise ValueError('Не удалось декодировать как {} последовательность: {}'
                                 .format('|'.join(encodings), xs))
        elif isinstance(xs, str):
            return cls(xs)
        else:
            raise TypeError('xs: ожидалось AnyStr: {!r}'.format(type(xs)))


class Str(EncodedStr, Scalar):
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({str.__repr__(self)})'


SafeStr = Str.of


class Integer(int, Scalar):
    signed: bool = NotImplemented
    max_bit_length: int = NotImplemented
    min: int = NotImplemented
    max: int = NotImplemented

    @classmethod
    def of(cls, x: int) -> 'Integer':
        return cls(cls.validated(x))

    @classmethod
    def validated(cls, x: int) -> int:
        if not isinstance(x, int):
            raise TypeError('x: ожидалось int: {!r}'.format(type(x)))
        if not cls.min <= x <= cls.max:
            raise ValueError('x: ожидалось Int{}{}: {:#_x}'.format(cls.max_bit_length, 's' if cls.signed else '', x))
        return x


def ranged(cls: Type[Integer]) -> Type[Integer]:
    if not (hasattr(cls, 'min') and isinstance(cls.min, int)):
        cls.min = -2 ** (cls.max_bit_length - 1) if cls.signed else 0

    if not (hasattr(cls, 'max') and isinstance(cls.max, int)):
        cls.max = 2 ** (cls.max_bit_length - 1) - 1 if cls.signed else 2 ** cls.max_bit_length - 1

    return cls


@ranged
class Int(Integer):
    signed = True
    max_bit_length = 32
    fmt = ''

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({int.__repr__(self)})'


SafeInt = Int.of


@ranged
class UByte(Integer):
    signed = False
    max_bit_length = 8
    fmt = '#x'

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({int.__repr__(self)})'


SafeUByte = UByte.of


@ranged
class Long(Integer):
    signed = True
    max_bit_length = 64
    fmt = ''

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({int.__repr__(self)})'


SafeLong = Long.of
Number = Union[float, int]


class Float(float, Scalar):
    rel_tol = 1e-05
    abs_tol = 1e-08
    fmt = '.7g'

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({float.__format__(self, self.fmt)})'

    @classmethod
    def of(cls, x: Number) -> 'Float':
        return cls(cls.validated(x))

    @classmethod
    def validated(cls, x: Number) -> float:
        if not isinstance(x, (float, int)):
            raise TypeError('x: ожидалось float | int: {!r}'.format(type(x)))
        y = c_float(x).value
        if not isfinite(y):
            raise ValueError('x: разрешены только конечные числа')
        return y

    def __eq__(self, other: Number) -> bool:
        if self is other:
            return True
        if not isinstance(other, (float, int)):
            return NotImplemented
        return isclose(self, other, rel_tol=Float.rel_tol, abs_tol=Float.abs_tol)

    __hash__ = float.__hash__


SafeFloat = Float.of


class Vector(tuple, Parameter):
    type: Type[Union[Float, Int, UByte]] = NotImplemented
    size: int = NotImplemented

    def __repr__(self) -> str:
        fmt = self.type.fmt
        return f'{self.__class__.__name__}(({", ".join(map(lambda x: format(x, fmt), self))}))'

    @classmethod
    def of(cls, xs: Sequence[Number]) -> 'Vector':
        sz = len(xs)
        if sz != cls.size:
            raise TypeError('Ожидалось {} компонент: {}'.format(cls.size, sz))
        return cls(map(cls.type.validated, xs))

    def __eq__(self, other: Sequence[Union[float, int]]) -> bool:
        if self is other:
            return True
        if not len(self) == len(other):
            return False
        return all(self.type.__eq__(x, y) for x, y in zip(self, other))

    __hash__ = tuple.__hash__


class Int2(Vector):
    type = Int
    size = 2


SafeInt2 = Int2.of


class Int3(Vector):
    type = Int
    size = 3


SafeInt3 = Int3.of


class Color(Vector):
    type = UByte
    size = 4


SafeColor = Color.of


class Float2(Vector):
    type = Float
    size = 2


SafeFloat2 = Float2.of


class Float3(Vector):
    type = Float
    size = 3


SafeFloat3 = Float3.of


class Float4(Vector):
    type = Float
    size = 4


SafeFloat4 = Float4.of


class Float12(Vector):
    type = Float
    size = 12


SafeFloat12 = Float12.of


class Name(EncodedStr):
    of_root = None

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({str.__repr__(self)})'


SafeName = Name.of

Item = Tuple[Name, Value]
PairsGenOf = Callable[['Section'], Iterable[Item]]


class Size(NamedTuple):
    params_count: int
    blocks_count: int


D = TypeVar('D')


def typed_getters(*kls: Type[Value]):
    def make_typed_getter(type_: Type[Value]):
        def typed_getter(self, name: str, index: Optional[int] = 0, default: Union[Tuple[()], D] = None
                         ) -> Union[type_, Sequence[type_], D]:
            value = self.get(name, index, default)
            if value is default:
                return default
            pred = isinstance(value, type_) if isinstance(value, Value) else (value and isinstance(value[0], type_))

            return value if pred else default

        return typed_getter

    def decorator(cls: 'Section') -> 'Section':
        for k in kls:
            name = f'get_{k.__name__.lower()}'
            typed_getter = make_typed_getter(k)
            typed_getter.__name__ = name
            setattr(cls, name, typed_getter)

        cls.get_section = make_typed_getter(cls)

        return cls

    return decorator


@typed_getters(Float3)
class Section(Value, metaclass=abc.ABCMeta):
    @classmethod
    def of(cls, section: 'Section') -> 'Section':
        root = cls()
        for name, value in section.pairs():
            if isinstance(value, Section):
                value = cls.of(value)  # @r
            root.append((name, value))
        return root

    def append(self, item: Item) -> None:
        raise NotImplementedError

    def add(self, name: str, value: Value) -> None:
        raise NotImplementedError

    @overload
    def get(self, name: str, index: None = None, default: D = ()) -> Union[Sequence[Value], D]:
        pass

    @overload
    def get(self, name: str, index: int = 0, default: D = None) -> Union[Value, D]:
        pass
    
    def get(self, name: str, index: Optional[int] = 0, default: D = None) -> Union[Value, Sequence[Value], D]:
        raise NotImplementedError

    def pairs(self) -> Iterable[Item]:
        raise NotImplementedError

    def check_cycle(self) -> None:
        raise NotImplementedError


# todo: ограничить уровень вложенности секций до 512
class DictSection(OrderedDict, Section):
    def append(self, item: Item) -> None:
        """Небезопасное добавление пары в секцию."""

        name, value = item
        if name not in self:
            self[name] = []

        self[name].append(value)

    def add(self, name: str, value: Value) -> None:
        """Добавление пары в секцию.

        :param name: Имя формируемой пары.
        :param value: Значение формируемой пары.
        :raises SectionError: Типы значений в мультизначении различны.
        """

        if not isinstance(name, EncodedStr):
            name = Name.of(name)
        elif isinstance(name, Str):
            name = Name(name)

        values = super().get(name)
        if values:
            fst_type = type(values[0])
            type_ = type(value)
            if fst_type is not type_:
                raise SectionError('Ожидалось {}: {}'.format(fst_type, type_))

        self.append((name, value))

    def get(self, name: str, index: Optional[int] = 0, default: Any = None) -> Union[Value, Sequence[Value], Any]:
        """Значение или значения в мультизначении по имени и индексу."""

        if index is None:
            try:
                return self[name]
            except KeyError:
                return () if default is None else default
        elif isinstance(index, int):
            try:
                return self[name][index]
            except (KeyError, IndexError):
                return default
        else:
            raise TypeError('index: ожидалось int | None: {!r}'.format(type(index)))

    def pairs(self) -> Iterable[Item]:
        """Пары в порядке добавления первого имени."""

        for name, values in self.items():
            if len(values) == 1:
                yield name, values[0]
            else:
                for value in values:
                    yield name, value

    def sorted_pairs(self) -> Iterable[Item]:
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

    def bfs_pairs_gen(self, pairs_of: PairsGenOf) -> Iterable[Item]:
        """
        Генератор пар при обходе секции в ширину с параметром.

        :param pairs_of: генератор потомков на уровне
        :return: генератор пар при обходе секции в ширину
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

    def bfs_sorted_pairs(self) -> Iterable[Item]:
        """Генератор пар при обходе секции в ширину."""

        yield from self.bfs_pairs_gen(lambda s: s.sorted_pairs())

    def names_dfs_nlr_rec(self) -> Iterable[Name]:
        """Генератор имен при обходе секции в глубину, рекурсивная версия."""

        for name, values in self.items():
            yield name
            for value in values:
                if isinstance(value, DictSection):
                    yield from DictSection.names_dfs_nlr_rec(value)  # @r

    names = names_dfs_nlr_rec

    def strings_dfs_nlr_rec(self) -> Iterable[Str]:
        """Генератор строк при обходе секции в глубину, рекурсивная версия."""

        for name, values in self.items():
            for value in values:
                if isinstance(value, DictSection):
                    yield from DictSection.strings_dfs_nlr_rec(value)  # @r
                elif isinstance(value, Str):
                    yield value

    strings = strings_dfs_nlr_rec

    def size(self) -> Size:
        """Размер секции на уровне.

        :return: (число параметров, число секций)
        """

        params_count, sections_count = 0, 0
        for name, value in self.pairs():
            if isinstance(value, Parameter):
                params_count += 1
            elif isinstance(value, Section):
                sections_count += 1

        return Size(params_count, sections_count)

    def check_cycle(self) -> None:
        """
        Проверка секции на цикл.

        :raises CycleError: найден цикл
        """

        def g(section: Section, ids: Set[int]) -> None:
            """
            :param section: проверяемая секция
            :param ids: id верхних уровней
            :raises CycleError: найден цикл
            """

            for name, value in section.pairs():
                if isinstance(value, Section):
                    id_ = id(value)
                    if id_ in ids:
                        raise CycleError
                    else:
                        ids.add(id_)
                        g(value, ids)
                        ids.remove(id_)

        g(self, {id(self)})

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}([{", ".join(map(repr, self.items()))}])'


class Command(tuple):
    prefix = "@"
    sep = ':'


class Comment(Command):
    prefix = Command.prefix + 'comment'
    name: ClassVar[Name] = ...

    def __new__(cls, value: str) -> 'Comment':
        value = Str(value)
        return super().__new__(cls, (cls.name, value))

    @property
    def text(self) -> str:
        return self[1]

    @classmethod
    def _check(cls, text: str) -> None:
        raise NotImplementedError

    @classmethod
    def of(cls, text: str) -> 'Comment':
        cls._check(text)
        return cls(text)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({str.__repr__(self[1])})'


class LineComment(Comment):
    """
    Строчный комментарий C++.

    // text
    """

    name = Name(Comment.prefix + 'CPP')

    @classmethod
    def _check(cls, text: str) -> None:
        if '\n' in text or '\r' in text:
            raise ValueError('Строчный комментарий содержит перенос строки: {!r}'.format(text))


SafeLineComment = LineComment.of


class BlockComment(Comment):
    """
    Блочный комментарий C.

     /*\n
     text\n
     */
    """

    name = Name(Comment.prefix + 'C')

    @classmethod
    def _check(cls, text: str) -> None:
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
    special_prefixes = '#', ':'
    path_seps = '/', '\\'
    default_path_sep = '/'

    def __new__(cls, value: str) -> 'Include':
        if not value:
            raise ValueError("Пустой путь.")
        if not isinstance(value, Str):
            value = Str(value)
        return super().__new__(cls, (cls.name, value))

    @property
    def path(self) -> Str:
        return self[1]

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({str.__repr__(self[1])})'


ItemPred = Callable[[Item], bool]


class ListSection(list, Section):
    """
    Представление текста без учета разделителей пар. Пары с сохранением порядка.
    """

    def add(self, name: str, value: Value) -> None:
        """Добавление пары в секцию.

        :param name: Имя формируемой пары.
        :param value: Значение формируемой пары.
        :raises SectionError: Типы значений в мультизначении различны.
        """

        if not isinstance(name, EncodedStr):
            name = Name.of(name)
        elif isinstance(name, Str):
            name = Name(name)

        for n, v in self:
            if n == name:
                fst_type = type(v)
                type_ = type(value)
                if fst_type is not type_:
                    raise SectionError('Ожидалось {}: {}'.format(fst_type, type_))
                break

        self.append((name, value))

    def add_comment(self, text: str) -> None:
        ctor = BlockComment if ('\n' in text or '\r' in text) else LineComment
        comment = ctor(text)
        self.append(comment)

    def pairs(self) -> Iterable[Item]:
        return iter(self)

    def get_index(self, p: ItemPred) -> Optional[int]:
        """Индекс первой пары, для которой выполняется предикат p."""

        for i, item in enumerate(self):
            if p(item):
                return i
        return None

    def get_indices(self, p: ItemPred) -> Sequence[int]:
        """Индексы пар, удовлетворяющих предикату p."""

        return tuple(i for i, item in enumerate(self) if p(item))

    def get_item(self, p: ItemPred) -> Optional[Item]:
        """Первая пара, удовлетворяющая предикату p."""

        for item in self:
            if p(item):
                return item
        return None

    def get_items(self, p: ItemPred) -> Sequence[Item]:
        """Пары, удовлетворяющие предикату p."""

        return tuple(filter(p, self))

    def set_item(self, p: ItemPred, item: Item):
        """Замена первой пары, удовлетворяющей предикату p."""

        i = self.get_index(p)
        if i is not None:
            super().__setitem__(i, item)

    def get(self, name: str, index: Optional[int] = 0, default: Any = None) -> Union[Value, Sequence[Value], Any]:
        """Значение или значения в мультизначении по имени и индексу."""

        if index is None:
            values = tuple(v for n, v in self if n == name)
            if not values and default is not None:
                return default
            return values
        elif isinstance(index, int):
            i = 0
            for n, v in self:
                if n == name and i == index:
                    return v
            return default
        else:
            raise TypeError('index: ожидалось int | None: {!r}'.format(type(index)))

    def remove_comments(self) -> None:
        indices = []
        for i, (n, v) in enumerate(self.pairs()):
            if n in (LineComment.name, BlockComment.name):
                indices.append(i)
            elif isinstance(v, ListSection):
                v.remove_comments()  # @r
        for i in reversed(indices):
            del self[i]

    def include_files(self, cdk_path: Optional[Path] = None, root_path: Optional[Path] = None) -> None:
        raise NotImplementedError

    def __call__(self) -> DictSection:
        """
        Выполнение команд, удаление комментариев.
        """

        raise NotImplementedError

    def check_cycle(self) -> None:
        """
        Проверка секции на цикл.

        :raises CycleError: найден цикл
        """

        raise NotImplementedError
