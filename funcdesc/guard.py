import typing as T
import functools
import types

from .desc import Value, Description
from .parse import parse_func


class CheckError(Exception):
    pass


class SideEffectError(Exception):
    pass


TF2 = T.TypeVar("TF2", bound=T.Callable)


class Guard(T.Generic[TF2]):
    def __init__(
            self,
            func: TF2,
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
            self._check_inputs(pass_in, errors)
        res = self.func(*args, **kwargs)
        if self.check_outputs:
            self._check_outputs(res, errors)
        if self.check_side_effect:
            self._check_side_effects(pass_in, res, errors)
        return res

    def _check_inputs(self, pass_in: dict, errors: list):
        for val in self.desc.inputs:
            self._check_value(val, pass_in[val.name], errors)
        if len(errors) > 0:
            raise CheckError(errors)

    def _check_outputs(self, res: T.Union[T.Any, T.Tuple], errors: list):
        if isinstance(res, tuple):
            if len(res) != len(self.desc.outputs):
                raise CheckError(
                    f"Output num({len(res)}) not match the"
                    f" description outputs num({len(self.desc.outputs)})"
                )
            for idx, val in enumerate(self.desc.outputs):
                self._check_value(val, res[idx], errors)
        else:
            if len(self.desc.outputs) != 1:
                raise CheckError(
                    "Output num(1) not match the"
                    f" description outputs num({len(self.desc.outputs)})"
                )
            val = self.desc.outputs[0]
            self._check_value(val, res, errors)
        if len(errors) > 0:
            raise CheckError(errors)

    def _check_value(
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

    def _check_side_effects(
            self, pass_in: dict,
            res: T.Union[tuple, T.Any], errors: list):
        if len(self.desc.side_effects) == 0:
            return
        in_dict: T.Dict[T.Union[int, str], T.Any] = {}
        for i, v in enumerate(self.desc.inputs):
            in_dict[i] = pass_in[v.name]
            in_dict[v.name] = pass_in[v.name]
        rtn_dict: T.Dict[T.Union[int, str], T.Any]
        if self.check_outputs:
            if isinstance(res, tuple):
                rtn_dict = {}
                for i, v in enumerate(self.desc.outputs):
                    rtn_dict[i] = res[i]
                    rtn_dict[v.name] = res[i]
            else:
                rtn_dict = {
                    self.desc.outputs[0].name: res,
                    0: res,
                }
        else:
            rtn_dict = {}
        for e in self.desc.side_effects:
            if not e.check(in_dict, rtn_dict):
                err = SideEffectError(
                    f"Error occured when check side effect: {self}"
                )
                errors.append(err)
        if len(errors) > 0:
            raise CheckError(errors)

    def __get__(self, obj, objtype):
        """Allow use on instance method."""
        if not hasattr(self, "_bounded"):  # bound only once
            target_func = self.func
            bound_mth = types.MethodType(target_func, obj)
            self.func = bound_mth
            self.desc.inputs.pop(0)
            self._bounded = True
        return self


def make_guard(
        func: T.Optional[TF2] = None,
        *,
        check_inputs: bool = True,
        check_outputs: bool = True,
        check_side_effect: bool = False,
        check_type: bool = True,
        check_range: bool = True,
        ) -> TF2:
    kwargs = {
        "check_inputs": check_inputs,
        "check_outputs": check_outputs,
        "check_side_effect": check_side_effect,
        "check_type": check_type,
        "check_range": check_range,
    }
    if func is None:
        return functools.partial(make_guard, **kwargs)  # type: ignore
    return Guard(func, **kwargs)  # type: ignore
