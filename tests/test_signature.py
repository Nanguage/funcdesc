import typing as T
import inspect
from funcdesc.mark import (
    sign_parameters, sign_return,
    copy_signature
)
from funcdesc import parse_func
from funcdesc.parse import parse_signature


def test_compose_signature():
    def test_for_func(f):
        desc = parse_func(f)
        sig = desc.compose_signature()
        desc1 = parse_signature(sig)
        assert all([
            (v.name == v1.name) and
            (v.range == v1.range) and
            (v.type == v1.type)
            for v, v1 in zip(desc.inputs, desc1.inputs)
        ])
        assert all([
            (v.name == v1.name) and
            (v.range == v1.range) and
            (v.type == v1.type)
            for v, v1 in zip(desc.outputs, desc1.outputs)
        ])

    def h():
        pass
    desc = parse_func(h)
    sig = desc.compose_signature()
    assert sig.return_annotation is inspect._empty
    test_for_func(h)

    def f2() -> None:
        pass
    test_for_func(f2)

    def f(a: int) -> str:
        return str(a)
    test_for_func(f)

    def g(a: int, b: int = 1) -> T.Tuple[int, int]:
        return a, b
    test_for_func(g)


def test_sign_parameters():
    @sign_parameters("a", ("b", int), ("c", int, 10))
    def f(*args) -> int:
        return sum(args)

    # The signature of `f` is changed
    sig = inspect.signature(f)
    assert len(sig.parameters) == 3
    assert sig.parameters["a"].annotation is inspect._empty
    assert sig.parameters["b"].annotation is int
    assert sig.parameters["c"].default == 10


def test_sign_return():
    @sign_return(str)
    def f(a: int):
        return str(a)

    # The signature of `f` is changed
    sig = inspect.signature(f)
    assert sig.return_annotation is str


def test_copy_signature():
    def f(a: int) -> str:
        return str(a)

    @copy_signature(f)
    def g(b):
        return str(b)

    # The signature of `g` is copied from `f`
    sig = inspect.signature(g)
    assert sig.parameters["a"].annotation is int
    assert sig.return_annotation is str
