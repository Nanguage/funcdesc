import typing as T
from funcdesc.mark import Val, Outputs, mark_input, mark_output
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

    def func3(a: Val[int, [0, 10]]) -> Val[int]:
        return a + 1

    desc_func3 = parse_func(func3)
    assert desc_func3.inputs[0].range == [0, 10]

    def func4(a: Val[int, [0, 10]]) -> Outputs[int, int]:
        return a, a

    desc_func4 = parse_func(func4)
    assert len(desc_func4.outputs) == 2

    def func5(a: Val[int, [0, 10]]) -> T.Tuple[int, int]:
        return a, a

    desc_func5 = parse_func(func5)
    assert len(desc_func5.outputs) == 2


def test_mark():
    @mark_input(0, range=[0, 10])
    @mark_input("b", range=[10, 20])
    @mark_output(0, range=[0, 30])
    def add(a: int, b: int) -> int:
        return a + b

    desc_add = parse_func(add)
    assert desc_add.inputs[0].type is int
    assert desc_add.inputs[0].range == [0, 10]
    assert desc_add.inputs[1].range == [10, 20]
    assert desc_add.outputs[0].range == [0, 30]
