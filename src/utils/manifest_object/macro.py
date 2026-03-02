from typing import Generator

from utils.manifest_object.manifest_object import ManifestObject


class MacroArgument:
    def __init__(self, data: dict):
        self.data = data

    @property
    def name(self) -> str:
        return self.data.get("name")

    @property
    def type(self) -> str | None:
        return self.data.get("name")

    @property
    def description(self) -> str | None:
        return self.data.get("description")


class Macro(ManifestObject):
    def filter_by_resource_type(self) -> bool:
        return self.data.get("resource_type") == "macro"

    @property
    def patch_path(self) -> str:
        return self.data["patch_path"]

    @property
    def arguments(self) -> Generator[MacroArgument, None, None]:
        return (
            MacroArgument(data=argument_data)
            for argument_data in self.data.get("arguments", [])
        )

    @property
    def macro_sql(self) -> str:
        return self.data["macro_sql"]
