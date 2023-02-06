from funcdesc.mark import Val, Outputs
from funcdesc.desc import Value
from funcdesc.parse import parse_func


def test_mark_Val():
    v = Val[int, [0, 10]]
    assert isinstance(v, Value)
    assert v.type is int
    assert v.range == [0, 10]

    v = Val(int, [0, 10])
    assert isinstance(v, Value)
    assert v.type is int
    assert v.range == [0, 10]


def test_mark_outputs():
    outs = Outputs[Val[int], Val[int]]
    assert isinstance(outs, list)
    assert len(outs) == 2


def test_parse_function():
    def func1(a: int) -> int:
        return a + 1

    desc_func1 = parse_func(func1)
    assert len(desc_func1.inputs) == 1
    assert desc_func1.inputs[0].type is int

    def func2(a: int, b: int = 1) -> int:
        return a + b

    desc_func2 = parse_func(func2)
    assert len(desc_func2.inputs) == 2
    assert desc_func2.inputs[1].default == 1
