import typing as t
from ctypes import c_float
from collections import OrderedDict, deque
from math import isfinite, isclose


__all__ = ['Value', 'Parameter', 'Vector', 'Bool', 'true', 'false', 'Str', 'Float', 'Float2', 'Float3', 'Float4',
           'Name', 'Section', 'Int', 'Long', 'UByte', 'Int2', 'Int3', 'Color', 'Float2', 'Float3', 'Float4', 'Float12',
           'EncodedStr', 'Var', 'method', 'floatstr']


class Var:
    __slots__ = ('value', )

    def __init__(self, init):
        self.value = init

    def __repr__(self):
        return f'{self.__class__.__name__}({self.value!r})'


def method(cls):
    def decorator(f):
        setattr(cls, f.__name__, f)
        return f

    return decorator


def floatstr(o):
    if int(o) == o:
        return float.__repr__(o)
    else:
        return format(o, '.7g')


class Value:
    pass


class Parameter(Value):
    pass


class Scalar(Parameter):
    pass


class Bool(int, Scalar):
    def __repr__(self):
        return 'true' if self else 'false'


true = Bool(1)
false = Bool(0)


class EncodedStr(str):
    encodings = ('utf8', 'cp1251')

    @classmethod
    def of(cls, xs, encodings=None):
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
    def __repr__(self):
        return f'{self.__class__.__name__}({str.__repr__(self)})'


SafeStr = Str.of


class Integer(int, Scalar):
    signed = NotImplemented
    max_bit_length = NotImplemented
    min = NotImplemented
    max = NotImplemented

    def __new__(cls, x):
        return super().__new__(cls, x)

    @classmethod
    def of(cls, x):
        return cls(cls.validated(x))

    @classmethod
    def validated(cls, x):
        if not isinstance(x, int):
            raise TypeError('x: ожидалось int: {!r}'.format(type(x)))
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
    signed = True
    max_bit_length = 32
    fmt = ''

    def __repr__(self):
        return f'{self.__class__.__name__}({int.__repr__(self)})'


SafeInt = Int.of


@ranged
class UByte(Integer):
    format = '#x'
    signed = False
    max_bit_length = 8
    fmt = '#x'

    def __repr__(self):
        return f'{self.__class__.__name__}({int.__repr__(self)})'


SafeUByte = UByte.of


@ranged
class Long(Integer):
    signed = True
    max_bit_length = 64
    fmt = ''

    def __repr__(self):
        return f'{self.__class__.__name__}({int.__repr__(self)})'


SafeLong = Long.of


class Float(float, Scalar):
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
            raise TypeError('x: ожидалось float | int: {!r}'.format(type(x)))
        y = c_float(x).value
        if not isfinite(y):
            raise ValueError('x: разрешены только конечные числа')
        return y

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, (float, int)):
            return NotImplemented
        return isclose(self, other, rel_tol=self.rel_tol, abs_tol=self.abs_tol)


SafeFloat = Float.of


class Vector(tuple, Parameter):
    type = NotImplemented
    size = NotImplemented

    def __new__(cls, xs):
        return super().__new__(cls, xs)

    def __repr__(self):
        fmt = self.type.fmt
        return f'{self.__class__.__name__}(({", ".join(map(lambda x: format(x, fmt), self))}))'

    @classmethod
    def of(cls, xs):
        sz = len(xs)
        if sz != cls.size:
            raise TypeError('Ожидалось {} компонент: {}'.format(cls.size, sz))
        return cls(map(cls.type.validated, xs))

    def __eq__(self, other):
        if self is other:
            return True
        if len(self) != len(other):
            return False
        for x, y in zip(self, other):
            if x != y:
                return False
        return True

    def __hash__(self):
        return super().__hash__()


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
    def __repr__(self):
        return f'{self.__class__.__name__}({str.__repr__(self)})'


SafeName = Name.of
ItemT = t.Tuple[Name, Value]
ItemsGenT = t.Generator[ItemT, None, None]
NamesGenT = t.Generator[Name, None, None]
ItemsGenOfT = t.Callable[['Section'], t.Iterable[ItemT]]


class Section(OrderedDict, Value):
    # todo: избежать цикла
    def append(self, name: Name, value: Value):
        if name not in self:
            self[name] = []
        self[name].append(value)

    def add(self, name: str, value: Value):
        if not isinstance(name, EncodedStr):
            name = Name.of(name)
        elif isinstance(name, Str):
            name = Name(name)

        self.append(name, value)

    def getf(self, name: Name, default=None) -> t.Optional[Value]:
        try:
            return self[name][0]
        except (IndexError, KeyError):
            return default

    def pairs(self) -> t.Generator[ItemT, None, None]:
        """(name, value) items"""

        return ((n, v) for n, vs in self.items() for v in vs)

    def reversed_pairs(self) -> t.Generator[ItemT, None, None]:
        """(name, value) reversed items"""

        return ((n, v) for n, vs in reversed(self.items()) for v in reversed(vs))

    def sorted_pairs(self) -> t.Generator[ItemT, None, None]:
        """sorted (name, value) items,
        parameters then sections
        """

        sections_pairs = []
        for item in self.pairs():
            value = item[1]
            if isinstance(value, Section):
                sections_pairs.append(item)
            else:
                yield item

        yield from sections_pairs

    def bfs_pairs_gen(self, pairs_of: ItemsGenOfT) -> ItemsGenT:
        queue = deque()
        queue.append((None, self))

        while queue:
            item = queue.popleft()
            yield item
            value = item[1]
            if isinstance(value, Section):
                for item in pairs_of(value):
                    queue.append(item)

    def bfs_sorted_pairs(self) -> ItemsGenT:
        yield from self.bfs_pairs_gen(lambda s: s.sorted_pairs())

    def dfs_nlr_pairs_gen(self, reversed_pairs_of: ItemsGenOfT) -> ItemsGenT:
        stack = deque()
        stack.append((None, self))

        while stack:
            item = stack.popleft()
            yield item
            value = item[1]
            if isinstance(value, Section):
                for item in reversed_pairs_of(value):
                    stack.insert(0, item)

    def dfs_nlr_pairs(self) -> ItemsGenT:
        yield from self.dfs_nlr_pairs_gen(lambda s: s.reversed_pairs())

    def names_dfs_nlr(self) -> NamesGenT:
        """names, preorder dfs"""

        ps = self.dfs_nlr_pairs()
        next(ps)
        return (p[0] for p in ps)

    names = names_dfs_nlr

    def size(self) -> t.Tuple[int, int]:
        params_count, sections_count = 0, 0
        for name, value in self.pairs():
            if isinstance(value, Parameter):
                params_count += 1
            elif isinstance(value, Section):
                sections_count += 1

        return params_count, sections_count

    def __repr__(self):
        return f'{self.__class__.__name__}([{", ".join(map(repr, self.items()))}])'
