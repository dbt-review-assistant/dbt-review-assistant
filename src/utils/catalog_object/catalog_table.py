"""Classes representing catalog tables."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, eq=True)
class CatalogColumn:
    """Represents a column in a catalog table.

    Attributes:
        data: dictionary of data from the catalog for the table column.
    """

    data: dict[str, Any]

    @property
    def type(self) -> str:
        """The type of the column."""
        return self.data["type"]

    @property
    def index(self) -> int:
        """The positional index of the column."""
        return self.data["index"]

    @property
    def name(self) -> str:
        """The name of the column."""
        return self.data["name"]

    @property
    def comment(self) -> str | None:
        """Any comment on the column."""
        return self.data.get("comment")


@dataclass(frozen=True, eq=True)
class CatalogTable:
    """Represents a catalog table.

    Attributes:
        data: dictionary of data from the catalog for the table.
    """

    data: dict[str, Any]

    @property
    def metadata(self) -> dict[str, Any]:
        """The metadata of the table."""
        return self.data["metadata"]

    @property
    def stats(self) -> dict[str, Any]:
        """The stats of the table."""
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
        """Any comment on the table."""
        return self.metadata.get("comment")

    @property
    def type(self) -> str | None:
        """The type of the table."""
        return self.metadata.get("type")

    @property
    def schema(self) -> str:
        """The schema name of the table."""
        return self.metadata["schema"]

    @property
    def name(self) -> str:
        """The name of the table."""
        return self.metadata["name"]

    @property
    def database(self) -> str | None:
        """The database name of the table."""
        return self.metadata.get("database")

    @property
    def owner(self) -> str | None:
        """The owner name of the table."""
        return self.metadata.get("owner")

    @property
    def columns(self) -> dict[str, CatalogColumn]:
        """The columns of the table.

        Returns:
            a dictionary mapping unique IDs to CatalogColumn instances.
        """
        return {
            f"{self.unique_id}.{column_name}": CatalogColumn(column_data)
            for column_name, column_data in self.data.get("columns", {}).items()
        }
