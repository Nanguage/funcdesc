import pytest

import typing as T
from funcdesc.mark import (
    Val, Outputs, mark_input, mark_output, mark_side_effect
)
from funcdesc.desc import Value, SideEffect, Description
from funcdesc.parse import parse_func
from funcdesc.guard import make_guard, Guard, CheckError
from funcdesc.utils.json import DescriptionJSONEncoder


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
    def func0():
        pass

    desc_func0 = parse_func(func0)
    assert len(desc_func0.inputs) == 0
    assert len(desc_func0.outputs) == 1
    assert desc_func0.outputs[0].type is type(None)  # noqa
    assert len(desc_func0.side_effects) == 0

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
    assert desc_func4.outputs[0].name == "output_0"
    assert desc_func4.outputs[1].name == "output_1"

    def func5(a: Val[int, [0, 10]]) -> T.Tuple[int, int]:
        return a, a

    desc_func5 = parse_func(func5)
    assert len(desc_func5.outputs) == 2

    @mark_output("ret", range=[0, 10])
    def func6() -> Val(int, name="ret"):  # noqa
        return 10

    desc_func6 = parse_func(func6)
    assert desc_func6.outputs[0].name == "ret"

    @mark_output(0, type=str)
    @mark_output(1, type=int)
    def func7():
        return "1", 1

    desc_func7 = parse_func(func7)
    assert desc_func7.outputs[0].type is str
    assert desc_func7.outputs[1].type is int

    @mark_output('out', type=str)
    def func8():
        return "1"

    desc_func8 = parse_func(func8)
    assert desc_func8.outputs[0].type is str

    @mark_output(0, type=str)
    @mark_output('a', type=int)
    def func9():
        return "1", 1

    with pytest.raises(ValueError):
        parse_func(func9)


def test_mark():
    @mark_input(0, range=[0, 10])
    @mark_input("b", range=[10, 20])
    @mark_output(0, range=[0, 30])
    @mark_side_effect(SideEffect("Print a string"))
    def add(a: int, b: int) -> int:
        print("add")
        return a + b

    desc_add = parse_func(add)
    assert desc_add.inputs[0].type is int
    assert desc_add.inputs[0].range == [0, 10]
    assert desc_add.inputs[1].range == [10, 20]
    assert desc_add.outputs[0].range == [0, 30]
    assert isinstance(desc_add.side_effects[0], SideEffect)


def test_guard():

    @make_guard
    @mark_input(0, range=[0, 10])
    @mark_input("b", range=[10, 20])
    @mark_output(0, range=[0, 30])
    def add(a: int, b: int = 10) -> int:
        return a + b

    assert add(5, 11) == 16
    assert add(5, b=12) == 17
    assert add(5) == 15

    with pytest.raises(CheckError):
        add(-10, 1)

    @make_guard(check_outputs=True)
    @mark_input(0, range=[0, 10])
    @mark_input("b", range=[10, 20])
    @mark_output(0, range=[0, 30])
    def add2(a: int, b: int) -> int:
        return a + b + 100

    with pytest.raises(CheckError):
        add2(1, 11)

    def add3(a: int) -> int:
        return a + 3

    desc_add3 = parse_func(add3)
    desc_add3.inputs[0].range = [0, 10]
    add3_guard = Guard(add3, desc_add3)
    with pytest.raises(CheckError):
        add3_guard(11)

    @make_guard(check_outputs=True)
    def exchange(a: str, b: int) -> T.Tuple[int, str]:
        return b, a

    assert exchange("1", 2) == (2, "1")

    @make_guard(check_outputs=True)
    def bug_exchange(a: str, b: int) -> T.Tuple[int, str]:
        return a, b

    with pytest.raises(CheckError):
        bug_exchange("1", 2)

    @make_guard(check_outputs=True)
    def bug_exchange2(a: str, b: str) -> T.Tuple[str, str]:
        return a + b

    with pytest.raises(CheckError):
        bug_exchange2("1", "2")

    @make_guard(check_outputs=True)
    def bug_exchange3(a: str, b: str) -> T.Tuple[str, str, str]:
        return (b, a)

    with pytest.raises(CheckError):
        bug_exchange3("1", "2")

    @make_guard(check_side_effect=True)
    @mark_side_effect(SideEffect("test"))
    def func1():
        pass

    func1()

    @make_guard
    def func2(a):
        pass

    with pytest.raises(TypeError):
        func2()


def test_serialization():
    @mark_input(0, range=[0, 10], doc="the first input")
    @mark_input("b", range=[10, 20])
    @mark_output(0, range=[0, 30])
    @mark_side_effect(SideEffect("Print something"))
    def add(a, b: int = 2, words: T.Optional[str] = None) -> int:
        print(words)
        print("a + b")
        return a + b

    desc_add = parse_func(add)
    desc_add.to_json()

    e = DescriptionJSONEncoder()
    with pytest.raises(TypeError):
        e.default(1)

    # test deserialization
    desc_add = parse_func(add)
    desc_add_json = desc_add.to_json()
    desc_add.inputs[0].doc = "the first input"
    desc_add2 = Description.from_json(desc_add_json)
    assert desc_add == desc_add2


def test_serialization2():
    class Position:
        def __init__(self, x: int, y: int):
            self.x = x
            self.y = y

    def get_position(x: int, y: int) -> Position:
        return Position(x, y)

    desc = parse_func(get_position)
    ser = desc.to_json()
    desc2 = Description.from_json(ser, env=locals())
    assert desc == desc2
    with pytest.warns(UserWarning):
        Description.from_json(ser)


def test_serialization3():
    def get_list() -> list[int]:
        return [1, 2, 3]

    desc = parse_func(get_list)
    ser = desc.to_json()
    desc2 = Description.from_json(ser)
    assert desc == desc2

    def get_dict() -> T.Dict[str, int]:
        return {"a": 1, "b": 2, "c": 3}

    desc = parse_func(get_dict)
    ser = desc.to_json()
    desc2 = Description.from_json(ser)
    assert desc == desc2


def test_class_method():
    class A():

        @mark_input(1, range=[0, 10])
        def mth1(self, a: int, b: int) -> int:
            return a + b

        @mark_input('a', range=[0, 10])
        def mth2(self, a: int, b: int) -> int:
            return a + b

        @make_guard(check_inputs=True)
        @mark_input('a', range=[0, 10])
        def mth3(self, a: int, b: int) -> int:
            return a + b

    desc_mth1 = parse_func(A.mth1)
    assert desc_mth1.inputs[1].range == [0, 10]
    a = A()
    desc_a_mth2 = parse_func(a.mth2)
    assert desc_a_mth2.inputs[0].range == [0, 10]
    desc_a_mth1 = parse_func(a.mth1)
    assert desc_a_mth1.inputs[0].range == [0, 10]
    assert a.mth3(10, 20) == 30
    with pytest.raises(CheckError):
        a.mth3(-1, 10)


def test_desc_repr():
    @mark_side_effect(SideEffect("test"))
    def f1(a: Val[int, [0, 10]], b: int = 10) -> Outputs[int, int]:
        pass

    desc = parse_func(f1)
    print(desc)
