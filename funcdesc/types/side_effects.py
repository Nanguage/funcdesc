from pathlib import Path

from ..desc import SideEffect


class WriteFile(SideEffect):
    def __init__(self, path_template: str):
        self.path_template = path_template

    @property
    def description(self) -> str:
        return f"Write file to {self.path_template}"

    def check(self, inputs: dict, outputs: dict) -> bool:
        path = self.path_template.format(
            inputs=inputs, outputs=outputs)
        path_obj = Path(path)
        return path_obj.exists()
