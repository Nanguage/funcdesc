import types
import typing as T
import inspect

from .desc import Description, Value
from .mark import FUNC_MARK_STORE_KEY, FuncMarks


GenericAlias = T._GenericAlias  # type: ignore


def _update_val_by_marks(
        mark_idx: int, name: str,
        marks: T.Dict, val: Value
        ):
    if mark_idx in marks:
        store = marks[mark_idx].copy()
    elif name in marks:
        store = marks[name].copy()
    else:
        store = None

    if store is not None:
        val.kwargs.update(store.pop("attrs"))
        val.__dict__.update(store)


def parse_func_inputs(
        sig: inspect.Signature,
        is_method: bool,
        marks: T.Dict[T.Union[int, str], dict],
        ) -> T.List[Value]:
    inputs = []
    for idx, (name, param) in enumerate(sig.parameters.items()):
        ann = param.annotation
        if isinstance(ann, Value):
            val = ann
        elif ann is inspect._empty:
            val = Value(None)
        else:
            val = Value(ann)

        val.name = name

        # set default value
        if param.default is not inspect._empty:
            val.default = param.default

        # update by marks
        mark_idx = idx + 1 if is_method else idx
        _update_val_by_marks(mark_idx, name, marks, val)

        inputs.append(val)
    return inputs


def parse_func_outputs(
        sig: inspect.Signature,
        marks: T.Dict[T.Union[int, str], dict]
        ) -> T.List[Value]:
    outputs = []
    ret = sig.return_annotation

    def to_val(o):
        return o if isinstance(o, Value) else Value(o)

    val: Value
    if ret is inspect._empty:
        val = Value(type(None))
        outputs.append(val)
    elif isinstance(ret, Value):
        outputs.append(ret)
    elif isinstance(ret, list):
        outputs.extend([to_val(o) for o in ret])
    elif isinstance(ret, GenericAlias) and \
            (ret._name == "Tuple"):
        outputs.extend([to_val(o) for o in ret.__args__])
    else:
        val = Value(ret)
        outputs.append(val)

    # update by marks
    for idx, val in enumerate(outputs):
        if val.name == "?":
            val.name = f"output_{idx}"

        _update_val_by_marks(idx, val.name, marks, val)
    return outputs


def parse_func(func: T.Callable) -> Description:
    desc = Description()
    sig = inspect.signature(func)
    is_method = isinstance(func, types.MethodType)
    func_marks: T.Optional[FuncMarks] = func.__dict__.get(FUNC_MARK_STORE_KEY)
    if func_marks is None:
        func_marks = FuncMarks()
    inputs = parse_func_inputs(sig, is_method, func_marks.input_marks)
    desc.inputs = inputs
    outputs = parse_func_outputs(sig, func_marks.output_marks)
    desc.outputs = outputs
    desc.side_effects = func_marks.side_effect_marks
    return desc
