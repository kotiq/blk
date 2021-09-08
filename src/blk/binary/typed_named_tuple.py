from construct import NamedTuple, Struct, Sequence, Array, GreedyRange, NamedTupleError


class TypedNamedTuple(NamedTuple):
    """NamedTuple с явно заданной фабрикой cls."""

    def __init__(self, cls, subcon):
        if not isinstance(subcon, (Struct, Sequence, Array, GreedyRange)):
            raise NamedTupleError("subcon is neither Struct Sequence Array GreedyRange")
        super(NamedTuple, self).__init__(subcon)
        self.tuplename = cls.__name__
        self.tuplefields = cls._fields
        self.factory = cls
