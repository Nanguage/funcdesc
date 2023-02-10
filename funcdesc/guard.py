import typing as T
import functools

from .desc import Value, Description
from .parse import parse_func


class ValueCheckError(Exception):
    pass


class Guard():
    def __init__(
            self,
            func: T.Callable,
            desc: T.Optional[Description] = None,
            check_inputs: bool = True,
            check_outputs: bool = True,
            check_side_effect: bool = False,
            check_type: bool = True,
            check_range: bool = True,
            ) -> None:
        self.func = func
        functools.update_wrapper(self, func)
        if desc is None:
            desc = parse_func(func)
        self.desc = desc
        self.check_type = check_type
        self.check_range = check_range
        self.check_side_effect = check_side_effect
        self.check_inputs = check_inputs
        self.check_outputs = check_outputs

    def __call__(self, *args, **kwargs):
        pass_in = self.desc.parse_pass_in(args, kwargs)
        errors = []
        if self.check_inputs:
            for val in self.desc.inputs:
                self._check(val, pass_in[val.name], errors)
            if len(errors) > 0:
                raise ValueCheckError(errors)
        res = self.func(*args, **kwargs)
        if self.check_outputs:
            if isinstance(res, tuple):
                if len(res) != len(self.desc.outputs):
                    raise ValueCheckError(
                        f"Output num({len(res)}) not match the"
                        f" description outputs num({len(self.desc.outputs)})"
                    )
                for idx, val in enumerate(self.desc.outputs):
                    self._check(val, res[idx], errors)
            else:
                if len(self.desc.outputs) != 1:
                    raise ValueCheckError(
                        "Output num(1) not match the"
                        f" description outputs num({len(self.desc.outputs)})"
                    )
                val = self.desc.outputs[0]
                self._check(val, res, errors)
            if len(errors) > 0:
                raise ValueCheckError(errors)
        return res

    def _check(
            self,
            arg: Value,
            val: T.Any,
            errors: T.List[Exception]):
        try:
            if self.check_type:
                arg.check_type(val)
            if self.check_range:
                arg.check_range(val)
        except Exception as e:
            errors.append(e)


def make_guard(
        func: T.Optional[T.Callable] = None,
        *,
        check_inputs: bool = True,
        check_outputs: bool = False,
        check_side_effect: bool = False,
        check_type: bool = True,
        check_range: bool = True,
        ) -> T.Callable:
    kwargs = {
        "check_inputs": check_inputs,
        "check_outputs": check_outputs,
        "check_side_effect": check_side_effect,
        "check_type": check_type,
        "check_range": check_range,
    }
    if func is None:
        return functools.partial(make_guard, **kwargs)
    return Guard(func, **kwargs)  # type: ignore
