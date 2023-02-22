import typing as T

from .desc import Value, _NotDef, NotDef, T1, SideEffect
from .utils.misc import CreateByGetItem


Val = Value


class Outputs(metaclass=CreateByGetItem):
    def __new__(
            cls,
            *outputs,
            ):
        return list(outputs)


FUNC_MARK_STORE_KEY = "_funcdesc_marks"


class FuncMarks():
    def __init__(self) -> None:
        self.input_marks: T.Dict[T.Union[str, int], T.Dict] = dict()
        self.output_marks: T.Dict[T.Union[str, int], T.Dict] = dict()
        self.side_effect_marks: T.List[SideEffect] = []


TF1 = T.TypeVar("TF1")


def _mark_val_factory(store_key: T.Literal["input", "output"]):
    def add_when_not_default(dict_, key, val, default):
        if val != default:
            dict_[key] = val

    def mark_val(
            pos_or_name: T.Union[int, str],
            *,
            type: T.Optional[T.Type[T1]] = None,
            range: T.Optional[T.Any] = None,
            default: T.Union[_NotDef, T1] = NotDef,
            name: T.Optional[str] = None,
            **attrs) -> T.Callable[[TF1], TF1]:

        store = {}
        store['attrs'] = attrs
        add_when_not_default(store, "type", type, None)
        add_when_not_default(store, "range", range, None)
        add_when_not_default(store, "default", default, NotDef)
        add_when_not_default(store, "name", name, None)

        def wrap(func: TF1) -> TF1:
            func.__dict__.setdefault(FUNC_MARK_STORE_KEY, FuncMarks())
            marks: FuncMarks = func.__dict__[FUNC_MARK_STORE_KEY]
            if store_key == "input":
                marks.input_marks[pos_or_name] = store
            else:
                marks.output_marks[pos_or_name] = store
            return func
        return wrap

    return mark_val


mark_input = _mark_val_factory("input")
mark_output = _mark_val_factory("output")


def mark_side_effect(side_effect: SideEffect):

    def wrap(func: T.Callable) -> T.Callable:
        func.__dict__.setdefault(FUNC_MARK_STORE_KEY, FuncMarks())
        marks: FuncMarks = func.__dict__[FUNC_MARK_STORE_KEY]
        marks.side_effect_marks.append(side_effect)
        return func

    return wrap
