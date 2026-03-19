from dataclasses import dataclass
from typing import Generator, Any

from utils.manifest_object.manifest_object import ManifestObject, HasPatchPathMixin


@dataclass(frozen=True, eq=True)
class MacroArgument:
    data: dict[str, Any]

    @property
    def name(self) -> str | None:
        return self.data.get("name")

    @property
    def type(self) -> str | None:
        return self.data.get("type")

    @property
    def description(self) -> str | None:
        return self.data.get("description")


class Macro(ManifestObject, HasPatchPathMixin):
    @property
    def arguments(self) -> Generator[MacroArgument, None, None]:
        return (
            MacroArgument(data=argument_data)
            for argument_data in self.data.get("arguments", [])
        )

    @property
    def macro_sql(self) -> str:
        return self.data["macro_sql"]
