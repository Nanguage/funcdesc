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


T2 = T.TypeVar("T2")
FUNC_MARK_STORE_KEY = "_funcdesc_marks"


class FuncMarks():
    def __init__(self) -> None:
        self.input_marks: T.Dict[T.Union[str, int], T.Dict] = dict()
        self.output_marks: T.Dict[T.Union[str, int], T.Dict] = dict()


def _mark_val_factory(store_key: T.Literal["input", "output"]):
    def add_when_not_default(dict_, key, val, default):
        if val != default:
            dict_[key] = val

    def mark_val(
            pos_or_name: T.Union[int, str],
            type_: T.Optional[T.Type[T2]] = None,
            range_: T.Optional[T.Any] = None,
            default: T.Union[_NotDef, T2] = NotDef,
            name: T.Optional[str] = None,
            **attrs) -> T.Callable:

        add_when_not_default(attrs, "type_", type_, None)
        add_when_not_default(attrs, "range_", range_, None)
        add_when_not_default(attrs, "default", default, NotDef)
        add_when_not_default(attrs, "name", name, None)
        
        def wrap(func: T.Callable) -> T.Callable:
            func.__dict__.setdefault(FUNC_MARK_STORE_KEY, FuncMarks())
            marks: FuncMarks = func.__dict__[FUNC_MARK_STORE_KEY]
            if store_key == "input":
                marks.input_marks[pos_or_name] = attrs
            else:
                marks.output_marks[pos_or_name] = attrs
            return func
        return wrap

    return mark_val


mark_input = _mark_val_factory("input")
mark_output = _mark_val_factory("output")
