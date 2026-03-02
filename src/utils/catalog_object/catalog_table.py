from typing import Any


class CatalogColumn:
    def __init__(self, data: dict) -> None:
        self.data = data

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


class CatalogTable:
    def __init__(self, data: dict) -> None:
        self.data = data

    def __eq__(self, other: "CatalogTable") -> bool:
        return isinstance(other, CatalogTable) and self.data == other.data

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
    def type(self) -> str:
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
