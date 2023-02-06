import typing as T

from .desc import Value, _NotDef, NotDef, T1


class CreateByGetItem(type):
    def __getitem__(self, args):
        if isinstance(args, tuple):
            return self(*args)
        else:
            return self(args)


class Val(metaclass=CreateByGetItem):
    def __new__(
            cls,
            type_: T.Optional[T.Type[T1]] = None,
            range_: T.Optional[T.Any] = None,
            default: T.Union[_NotDef, T1] = NotDef,
            name: T.Optional[str] = None,
            ):
        return Value(type_, range_, default, name)


class Outputs(metaclass=CreateByGetItem):
    def __new__(
            cls,
            *outputs,
            ):
        return list(outputs)

