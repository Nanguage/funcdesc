import typing as T
import inspect

from .desc import Description, Value


def parse_func_inputs(sig: inspect.Signature) -> T.List[Value]:
    inputs = []
    for name, param in sig.parameters.items():
        ann = param.annotation
        if isinstance(ann, Value):
            val = ann
        elif ann is inspect._empty:
            val = Value(None, None, name=name)
        else:
            val = Value(ann, None, name=name)
        if param.default is not inspect._empty:
            val.default = param.default
        inputs.append(val)
    return inputs


def parse_func_outputs(sig: inspect.Signature) -> T.List[Value]:
    outputs = []
    ret = sig.return_annotation
    if isinstance(ret, Value):
        outputs.append(ret)
    elif isinstance(ret, list):
        outputs.extend(ret)
    else:
        val: Value = Value(ret)
        outputs.append(val)
    return outputs


def parse_func(func: T.Callable) -> Description:
    desc = Description()
    sig = inspect.signature(func)
    inputs = parse_func_inputs(sig)
    desc.inputs = inputs
    outputs = parse_func_outputs(sig)
    desc.outputs = outputs
    return desc
