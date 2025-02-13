from funcdesc.pydantic import parse_func_pydantic

from pydantic import BaseModel


def test_pydantic():
    def func(a: int, b: int) -> int:
        return a + b

    res = parse_func_pydantic(func)
    assert issubclass(res["inputs"], BaseModel)
    assert issubclass(res["outputs"], BaseModel)

    def func2(a: int, b: int = 10) -> int:
        return a + b

    res = parse_func_pydantic(func2)
    assert issubclass(res["inputs"], BaseModel)
    assert issubclass(res["outputs"], BaseModel)
