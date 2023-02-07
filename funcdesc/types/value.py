from pathlib import Path

from ..desc import Value


class ValueType(object):
    @staticmethod
    def check_type(val, type_):
        return True

    @staticmethod
    def check_range(val, range_):
        return True


class Selection(ValueType):
    @staticmethod
    def check_range(val, range_):
        return val in range_


class SubSet(ValueType):
    @staticmethod
    def check_range(val, range_):
        return all([v in range_ for v in val])


class InputPath(ValueType):
    @staticmethod
    def check_type(val, type_):
        return isinstance(val, str) or isinstance(val, Path)

    @staticmethod
    def check_range(val, range_):
        path = Path(val) if isinstance(val, str) else val
        return path.exists()


class OutputPath(ValueType):
    @staticmethod
    def check_type(val, type_):
        return isinstance(val, str) or isinstance(val, Path)


Value.register_range_check(Selection, Selection.check_range)
Value.register_range_check(SubSet, SubSet.check_range)
Value.register_type_check(InputPath, InputPath.check_type)
Value.register_range_check(InputPath, InputPath.check_range)
Value.register_type_check(OutputPath, OutputPath.check_type)
