from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, eq=True)
class CatalogColumn:
    data: dict[str, Any]

    @property
    def type(self) -> str:
        return self.data["type"]

    @property
    def index(self) -> int:
        return self.data["index"]

    @property
    def name(self) -> str:
        return self.data["name"]

    @property
    def comment(self) -> str | None:
        return self.data.get("comment")


@dataclass(frozen=True, eq=True)
class CatalogTable:
    data: dict[str, Any]

    @property
    def metadata(self) -> dict[str, Any]:
        return self.data["metadata"]

    @property
    def stats(self) -> dict[str, Any]:
        return self.data["stats"]

    @property
    def unique_id(self) -> str:
        """The unique_id of the CatalogTable instance.

        Developer note - in the v1 catalog.json schema this attribute is technically not required
        as per documentation, but there don't seem to be any scenarios where it can be missing
        in practice.
        """
        return self.data["unique_id"]

    @property
    def comment(self) -> str | None:
        return self.metadata.get("comment")

    @property
    def type(self) -> str | None:
        return self.metadata.get("type")

    @property
    def schema(self) -> str:
        return self.metadata["schema"]

    @property
    def name(self) -> str:
        return self.metadata["name"]

    @property
    def database(self) -> str | None:
        return self.metadata.get("database")

    @property
    def owner(self) -> str | None:
        return self.metadata.get("owner")

    @property
    def columns(self) -> dict[str, CatalogColumn]:
        return {
            f"{self.unique_id}.{column_name}": CatalogColumn(column_data)
            for column_name, column_data in self.data.get("columns", {}).items()
        }
