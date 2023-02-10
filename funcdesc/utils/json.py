import typing as T
import json


class DescriptionJSONEncoder(json.JSONEncoder):
    def default(self, o: T.Any) -> T.Any:
        from ..desc import Description, Value, SideEffect, _NotDef
        if isinstance(o, Description):
            return {
                "inputs": [self.default(v) for v in o.inputs],
                "outputs": [self.default(v) for v in o.outputs],
                "side_effects": [self.default(v) for v in o.side_effects],
            }
        elif isinstance(o, Value):
            return {
                "type": o.type.__name__ if o.type is not None else o.type,
                "range": o.range,
                "default": o.default,
            }
        elif isinstance(o, _NotDef):
            return "not_defined"
        elif isinstance(o, SideEffect):
            return {
                "type": o.__class__.__name__,
                "description": o.description,
            }
        else:
            return super().default(o)
