from funcdesc.parse import parse_func


def test_docstring():
    def func(a: int, b):
        """
        This is a test function.

        Args:
            a: The first argument.
            b (int): The second argument.

        Returns:
            int: The sum of the two arguments.
        """
        return a + b

    desc = parse_func(func, update_by_docstring=True)
    assert desc.inputs[0].doc == "The first argument."
    assert desc.inputs[1].type == int
    assert desc.inputs[1].doc == "The second argument."
    assert desc.outputs[0].doc == "The sum of the two arguments."
    assert desc.outputs[0].type == int

    def func2(a: int, b: int) -> int:
        """
        This is a test function.

        Args:
            a: The first argument.
            b: The second argument.

        """
        return a + b

    desc = parse_func(func2, update_by_docstring=True)
    assert desc.inputs[0].doc == "The first argument."
    assert desc.inputs[1].type == int
    assert desc.inputs[1].doc == "The second argument."
    assert desc.outputs[0].doc is None
    assert desc.outputs[0].type == int
