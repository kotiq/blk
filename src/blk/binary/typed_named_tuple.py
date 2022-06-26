from typing import Type, NamedTuple
import construct as ct


class TypedNamedTuple(ct.NamedTuple):
    """NamedTuple с явно заданной фабрикой cls."""

    def __init__(self, cls: Type[NamedTuple], subcon: ct.Construct) -> None:
        if not isinstance(subcon, (ct.Struct, ct.Sequence, ct.Array, ct.GreedyRange)):
            raise ct.NamedTupleError("subcon is neither Struct Sequence Array GreedyRange")
        super(ct.NamedTuple, self).__init__(subcon)
        self.tuplename = cls.__name__
        self.tuplefields = cls._fields
        self.factory = cls
