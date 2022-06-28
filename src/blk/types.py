import abc
from typing import Callable, Iterable, NamedTuple, Optional, Sequence, Set, Tuple, Type, Union, overload
from ctypes import c_float
from collections import OrderedDict, deque
from math import isfinite, isclose


__all__ = [
    'BlockComment',
    'Bool',
    'CloneLast',
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
    'LineComment',
    'ListSection',
    'Long',
    'Name',
    'Override',
    'Parameter',
    'Post',
    'Pre',
    'Section',
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


class CycleError(Exception):
    """Секция содержит цикл."""


class Var:
    __slots__ = ('value', )

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

Pair = Tuple[Name, Value]
ParameterPair = Tuple[Name, Parameter]
SectionPair = Tuple[Name, 'Section']
PairsGenOf = Callable[['Section'], Iterable[Pair]]


class Size(NamedTuple):
    params_count: int
    blocks_count: int


class Section(Value, metaclass=abc.ABCMeta):
    def append(self, name: Name, value: Value) -> None:
        raise NotImplementedError

    def add(self, name: str, value: Value) -> None:
        raise NotImplementedError

    def pairs(self) -> Iterable[Pair]:
        raise NotImplementedError

    def check_cycle(self) -> None:
        raise NotImplementedError


# todo: ограничить уровень вложенности секций до 512
class DictSection(OrderedDict, Section):
    def append(self, name: Name, value: Value) -> None:
        """Небезопасное добавление пары в секцию."""

        if name not in self:
            self[name] = []
        self[name].append(value)

    def add(self, name: str, value: Value) -> None:
        """Добавление пары в секцию."""

        if not isinstance(name, EncodedStr):
            name = Name.of(name)
        elif isinstance(name, Str):
            name = Name(name)

        self.append(name, value)

    def get_first(self, name: Name, default=None) -> Optional[Value]:
        """Первое значение в мультизначении по имени."""

        try:
            return self[name][0]
        except (IndexError, KeyError):
            return default

    def pairs(self) -> Iterable[Pair]:
        """Пары в порядке добавления первого имени."""

        for name, values in self.items():
            if len(values) == 1:
                yield name, values[0]
            else:
                for value in values:
                    yield name, value

    def sorted_pairs(self) -> Iterable[Pair]:
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

    def bfs_pairs_gen(self, pairs_of: PairsGenOf) -> Iterable[Pair]:
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

    def bfs_sorted_pairs(self) -> Iterable[Pair]:
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


class Item(NamedTuple):
    name: Name
    value: Value


class Command(Item):
    prefix = "@"
    sep = ':'


class Pre:
    pass


class Post:
    pass


class Include(Command, Pre):
    """
    include text
    """

    name = Name(Command.prefix + 'include')

    def __new__(cls, value: str) -> 'Include':
        value = Str(value)
        return super().__new__(cls, cls.name, value)

    @classmethod
    def like(cls, name: Name, value: Value) -> bool:
        return name == cls.name and isinstance(value, Str)

    @property
    def path(self):
        return self.value

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({str.__repr__(self.value)})'


class Comment(Command, Pre):
    prefix = Command.prefix + 'comment'

    def __new__(cls, value: str) -> 'Comment':
        value = Str(value)
        return super().__new__(cls, cls.name, value)

    @property
    def text(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({str.__repr__(self.value)})'


class LineComment(Comment):
    """
    // text
    """

    name = Name(Comment.prefix + 'CPP')

    @staticmethod
    def _check(text: str) -> None:
        if '\n' in text or '\r' in text:
            raise ValueError('Однострочный комментарий содержит перенос строки: {}'.format(text))

    @classmethod
    def of(cls, text: str) -> 'LineComment':
        cls._check(text)
        return cls(text)

    @classmethod
    def like(cls, name: Name, value: Value) -> bool:
        if name == cls.name and isinstance(value, Str):
            try:
                cls._check(value)
            except ValueError:
                return False
            else:
                return True
        return False


class BlockComment(Comment):
    """
    /*
    text
    */
    """

    name = Name(Comment.prefix + 'C')

    @classmethod
    def like(cls, name: Name, value: Value) -> bool:
        return name == cls.name and isinstance(value, Str)


# todo: при добавлении в секцию предупреждать в случае отсутствия include и target выше
class Targeted(Command, Post):
    def __new__(cls, name: str, value: Value) -> 'Targeted':
        name = Name(cls.prefix + name)
        return super().__new__(cls, name, value)

    @classmethod
    def like(cls, name: Name, value: Value) -> bool:
        return (
            name.startswith(cls.prefix)
            and name[len(cls.prefix):]
            and isinstance(value, Value)
        )

    @property
    def target(self) -> Name:
        return Name(self.name[len(self.prefix):])

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({str.__repr__(self.target)}, {self.value!r})'


class Override(Targeted):
    """
    Перегрузка первого значения.
    """

    prefix = Command.prefix + 'override' + Command.sep


class CloneLast(Targeted):
    """
    Копия последней пары.
    """

    prefix = Command.prefix + 'clone-last' + Command.sep


class ListSection(list, Section):
    """
    Представление текста без учета разделителей пар. Пары с сохранением порядка.
    """

    @classmethod
    def of(cls, m: DictSection) -> DictSection:
        raise NotImplementedError

    @overload
    def append(self, name: Name, value: Value) -> None:
        ...

    @overload
    def append(self, command: Command) -> None:
        ...

    def append(self, name_or_command: Union[Name, Command], maybe_value: Optional[Value] = None) -> None:
        if maybe_value is None:
            item = name_or_command
        else:
            item = Item(name_or_command, maybe_value)

        super().append(item)

    @overload
    def add(self, name: str, value: Value) -> None:
        ...

    @overload
    def add(self, command: Command) -> None:
        ...

    def add(self, name_or_command: Union[str, Command], maybe_value: Optional[Value] = None) -> None:
        """
        Добавление пары в секцию.
        """

        if isinstance(name_or_command, str) and maybe_value is not None:
            name = name_or_command
            if not isinstance(name, EncodedStr):
                name = Name.of(name)
            elif isinstance(name, Str):
                name = Name(name)
            self.append(name, maybe_value)
        elif isinstance(name_or_command, Command) and maybe_value is None:
            command = name_or_command
            self.append(command)
        else:
            raise ValueError('Недопустимая комбинация аргументов: {}, {}'.format(name_or_command, maybe_value))

    def pairs(self) -> Iterable[Pair]:
        return iter(self)

    def getindex(self, p: Callable[[Item], bool]) -> int:
        """
        Индекс первой пары, для которой выполняется предикат.

        :param p: предикат
        :return: индекс
        """

        for i, item in enumerate(self):
            if p(item):
                return i
        raise ValueError('Нет пар, удовлетворяющих предикату: {}'.format(p))

    def getindexes(self, p: Callable[[Item], bool]) -> Sequence[int]:
        return tuple(i for i, item in enumerate(self) if p(item))

    # здесь желателен двусвязный список, чтобы быстро перемещаться назад
    # def getlastindex(self, p: t.Callable[[Item], bool], index: int):
    #     j = None
    #     for i, item in enumerate(self):
    #         if i == index:
    #             break
    #         if p(item):
    #             j = i
    #     if j is not None:
    #         return j
    #     raise ValueError('Нет пар с индексом до {1}, удовлетворяющих предикату: {0}'.format(p, index))

    def getitem(self, p: Callable[[Item], bool]) -> int:
        for item in self:
            if p(item):
                return item
        raise ValueError('Нет пар, удовлетворяющих предикату: {}'.format(p))

    def getitems(self, p: Callable[[Item], bool]) -> Sequence[Item]:
        return tuple(filter(p, self))

    def setitem(self, p: Callable[[Item], bool], item: Item):
        i = self.getindex(p)
        super().__setitem__(i, item)

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
