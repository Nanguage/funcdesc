import pytest
import os

from funcdesc.guard import make_guard, ValueCheckError
from funcdesc.mark import mark_input, mark_output
from funcdesc.types.value import OneOf, SubSet, InputPath, OutputPath
from funcdesc.mark import Val


def test_oneof():
    big_list = [1, 2, 3, 4]

    @make_guard
    def add1(a: Val[OneOf, big_list]):
        return a + 1

    assert add1(1) == 2
    with pytest.raises(ValueCheckError):
        add1(-1)


def test_subset():
    big_list = [1, 2, 3, 4]

    @make_guard
    @mark_input("s", range=big_list)
    def all_add1(s: SubSet):
        return [v + 1 for v in s]

    assert all_add1([1, 2]) == [2, 3]
    with pytest.raises(ValueCheckError):
        all_add1([5, 5])


def test_path():
    @make_guard(check_outputs=True)
    @mark_input(0, type=InputPath)
    @mark_output(0, type=OutputPath)
    def func1(path, return_path: bool):
        if return_path:
            return path
        else:
            return 0

    exist_file = "a_exist_file.txt"
    with open(exist_file, 'w') as f:
        f.write("aaa")

    func1(exist_file, True)
    with pytest.raises(ValueCheckError):
        func1(exist_file, False)

    os.remove(exist_file)

    with pytest.raises(ValueCheckError):
        func1("a_not_exist_file.txt", True)
