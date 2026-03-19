"""Classes representing macro objects in the manifest file."""

from dataclasses import dataclass
from typing import Generator, Any

from utils.manifest_object.manifest_object import ManifestObject, HasPatchPathMixin


@dataclass(frozen=True, eq=True)
class MacroArgument:
    """Represents a macro argument in the manifest.

    Attributes:
        data: dictionary of data for the macro argument.
    """

    data: dict[str, Any]

    @property
    def name(self) -> str | None:
        """The name of the macro argument."""
        return self.data.get("name")

    @property
    def type(self) -> str | None:
        """The data type of the macro argument."""
        return self.data.get("type")

    @property
    def description(self) -> str | None:
        """The description of the macro argument."""
        return self.data.get("description")


class Macro(ManifestObject, HasPatchPathMixin):
    """Represents a macro in the manifest."""

    @property
    def arguments(self) -> Generator[MacroArgument, None, None]:
        """The macro's arguments.

        Yields:
            MacroArgument instances.
        """
        return (
            MacroArgument(data=argument_data)
            for argument_data in self.data.get("arguments", [])
        )

    @property
    def macro_sql(self) -> str:
        """The macro's raw SQL file definition code."""
        return self.data["macro_sql"]
