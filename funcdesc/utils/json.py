import typing as T
import warnings
import json

if T.TYPE_CHECKING:  # pragma: no cover
    from ..desc import Value, SideEffect, Description


NoneType = type(None)


class DescriptionJSONEncoder(json.JSONEncoder):
    def default(self, o: T.Any) -> T.Any:
        from ..desc import Description, Value, SideEffect, _NotDef
        if isinstance(o, Description):
            return {
                "inputs": [self.default(v) for v in o.inputs],
                "outputs": [self.default(v) for v in o.outputs],
                "side_effects": [self.default(v) for v in o.side_effects],
                "name": o.name,
                "doc": o.doc,
            }
        elif isinstance(o, Value):
            if o.type is None:
                t = None
            elif o.type.__module__ == "typing":
                t = str(o.type)
            elif isinstance(o.type, T.GenericAlias):  # type: ignore
                t = str(o.type)
            else:
                t = o.type.__name__
            return {
                "type": t,
                "range": o.range,
                "default": o.default,
                "name": o.name,
                "doc": o.doc,
            }
        elif isinstance(o, _NotDef):
            return "not_defined"
        elif isinstance(o, SideEffect):
            return {
                "description": o.description,
            }
        else:
            return super().default(o)


class DescriptionJSONDecoder(json.JSONDecoder):
    def decode_value(
            self,
            v: T.Dict[str, T.Any],
            env: T.Optional[T.Dict[str, T.Any]] = None
            ) -> "Value":
        from ..desc import Value, NotDef
        import typing

        if env is not None:
            env["typing"] = typing

        if isinstance(v["type"], str):
            try:
                t = eval(v["type"], env)
            except NameError:
                warnings.warn(
                    f"Failed to eval type {v['type']}, "
                    "using the original string as type."
                )
                t = v["type"]
        else:
            t = v["type"]

        r = v["range"]

        if v["default"] == "not_defined":
            d = NotDef
        else:
            d = v["default"]
        value = Value(
            type_=t,
            range_=r,
            default=d,
            name=v["name"],
            doc=v["doc"],
        )
        return value

    def decode_side_effect(
            self, v: T.Dict[str, T.Any]) -> "SideEffect":
        from ..desc import SideEffect
        return SideEffect(**v)

    def decode_description(
            self,
            s: str,
            env: T.Optional[T.Dict[str, T.Any]] = None
            ) -> "Description":
        from ..desc import Description
        jdict = super().decode(s)
        desc = Description()
        desc.name = jdict["name"]
        desc.doc = jdict["doc"]
        desc.inputs = [self.decode_value(v, env) for v in jdict["inputs"]]
        desc.outputs = [self.decode_value(v, env) for v in jdict["outputs"]]
        desc.side_effects = [
            self.decode_side_effect(v) for v in jdict["side_effects"]
        ]
        return desc

    def decode(self, *args, **kwargs) -> T.Any:
        return self.decode_description(*args, **kwargs)
