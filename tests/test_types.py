import typing as T
import pytest
import os

from funcdesc.guard import make_guard, CheckError
from funcdesc.mark import mark_input, mark_side_effect
from funcdesc.types.value import (
    OneOf, SubSet, InputPath, OutputPath, ValueType
)
from funcdesc.types.side_effects import WriteFile
from funcdesc.mark import Val


def test_value_type():
    v = ValueType()
    v.check_range(None, None)
    v.check_type(None, None)


def test_oneof():
    big_list = [1, 2, 3, 4]

    @make_guard
    def add1(a: Val[OneOf, big_list]):
        return a + 1

    assert add1(1) == 2
    with pytest.raises(CheckError):
        add1(-1)


def test_subset():
    big_list = [1, 2, 3, 4]

    @make_guard
    @mark_input("s", range=big_list)
    def all_add1(s: SubSet):
        return [v + 1 for v in s]

    assert all_add1([1, 2]) == [2, 3]
    with pytest.raises(CheckError):
        all_add1([5, 5])


def test_path():
    @make_guard(check_outputs=True)
    @mark_input(0, type=InputPath)
    def func1(path, return_path: bool) -> OutputPath:
        if return_path:
            return path
        else:
            return 0

    exist_file = "a_exist_file.txt"
    with open(exist_file, 'w') as f:
        f.write("aaa")

    func1(exist_file, True)
    with pytest.raises(CheckError):
        func1(exist_file, False)

    os.remove(exist_file)

    with pytest.raises(CheckError):
        func1("a_not_exist_file.txt", True)


def test_write_file_effect():
    test_name = "testtest"

    @make_guard(check_side_effect=True)
    @mark_side_effect(WriteFile("{inputs[name]}.txt"))
    def func1(name):
        with open(name+".txt", 'w') as f:
            f.write("aaa")

    func1(test_name)
    os.remove(test_name+".txt")

    @make_guard(check_side_effect=True)
    @mark_side_effect(WriteFile("{inputs[0]}.txt"))
    def func2(name):
        pass

    with pytest.raises(CheckError):
        func2(test_name)

    @make_guard(check_side_effect=True)
    @mark_side_effect(WriteFile("{outputs[1]}"))
    def func3(name) -> T.Tuple[str, str]:
        path = name + ".txt"
        with open(name+".txt", 'w') as f:
            f.write("aaa")
        return name, path

    func3(test_name)
    os.remove(test_name+".txt")
    print(func3.desc)

    @make_guard(check_side_effect=True, check_outputs=False)
    @mark_side_effect(WriteFile("{inputs[0]}.txt"))
    def func4(name):
        pass

    with pytest.raises(CheckError):
        func4(test_name)

    @make_guard(check_side_effect=True)
    def func5(name):
        pass

    func5(test_name)

    with open(test_name+".txt", 'w') as f:
        f.write("1")

    @make_guard(check_side_effect=True)
    @mark_side_effect(WriteFile("{inputs[name]}.txt"))
    def func6(name):
        with open(name+".txt", 'w') as f:
            f.write("aaa")

    with pytest.raises(CheckError):
        func6(test_name)
    os.remove(test_name+".txt")
