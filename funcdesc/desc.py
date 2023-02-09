import typing as T
from copy import copy

from .utils.json import DescriptionJSONEncoder


class _NotDef:
    pass


NotDef = _NotDef()


T1 = T.TypeVar("T1")


TypeChecker = T.Callable[[T.Any, type], bool]
RangeChecker = T.Callable[[T.Any, T.Any], bool]


class Value(T.Generic[T1]):
    type_to_range_checker: T.Dict[type, TypeChecker] = {}
    type_to_type_checker: T.Dict[type, RangeChecker] = {}

    def __init__(
            self,
            type_: T.Optional[T.Type[T1]] = None,
            range_: T.Optional[T.Any] = None,
            default: T.Union[_NotDef, T1] = NotDef,
            name: str = "?",
            ):
        self.name = name
        self.type = type_
        self.range = range_
        self.default = default

    @property
    def type_checker(self):
        return self.type_to_type_checker.get(self.type.__name__, None)

    @property
    def range_checker(self):
        return self.type_to_range_checker.get(self.type.__name__, None)

    @classmethod
    def register_range_check(cls, type, checker):
        cls.type_to_range_checker[type.__name__] = checker

    @classmethod
    def register_type_check(cls, type, checker=None):
        checker = checker or (lambda v, t: isinstance(v, t))
        cls.type_to_type_checker[type.__name__] = checker

    def check_type(self, val):
        if self.type_checker is not None:
            if not self.type_checker(val, self.type):
                raise TypeError(
                    f"Value {val} is not in valid type({self.type})")

    def check_range(self, val):
        if (self.range_checker is not None):
            if (not self.range_checker(val, self.range)):
                raise ValueError(
                    f"Value {val} is not in a valid range({self.range}).")

    def check(self, val):
        if (self.range_checker is None) and (self.type_checker is None):
            raise NotImplementedError(
                f"Not checker registered for type: {type}")
        self.check_type(val)
        self.check_range(val)


# register basic types
def _check_number_in_range(v, range):
    return (range is None) or (range[0] <= v <= range[1])


Value.register_type_check(str)
Value.register_range_check(int, _check_number_in_range)
Value.register_type_check(int)
Value.register_range_check(float, _check_number_in_range)
Value.register_type_check(float)
Value.register_type_check(bool)


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

    def parse_pass_in(self, args: tuple, kwargs: dict) -> T.Dict[str, T.Any]:
        """Get the pass in value of the func
        arguments according to the inputs description."""

        args_ = list(args)
        kwargs = copy(kwargs)
        res = {}
        for val in self.inputs:
            has_default = val.default is not NotDef
            name: str = val.name
            if len(args_) > 0:
                res[name] = args_.pop(0)
            elif (len(kwargs) > 0) and (name in kwargs):
                res[name] = kwargs.pop(name)
            else:
                if has_default:
                    res[name] = val.default
                else:
                    raise ValueError(
                        f"{name} is not provided and has no default value."
                    )
        return res

    def to_json(self) -> str:
        json_str = DescriptionJSONEncoder().encode(self)
        return json_str
