import typing as T


class _NotDef:
    pass


NotDef = _NotDef()


T1 = T.TypeVar("T1")


class Value(T.Generic[T1]):
    def __init__(
            self,
            type_: T.Optional[T.Type[T1]] = None,
            range_: T.Optional[T.Any] = None,
            default: T.Union[_NotDef, T1] = NotDef,
            name: T.Optional[str] = None,
            ):
        self.name = name
        self.type = type_
        self.range = range_
        self.default = default


class SideEffect():
    def __init__(self, description: str):
        self.description = description


class Description():
    def __init__(
            self,
            inputs: T.Optional[T.List[Value]] = None,
            outputs: T.Optional[T.List[Value]] = None,
            side_effects: T.Optional[T.List[SideEffect]] = None,
            ):
        self.inputs = [] if inputs is None else inputs
        self.outputs = [] if outputs is None else outputs
        self.side_effects = [] if side_effects is None else side_effects
