"""Check if the source column types match between the manifest and the catalog."""

from typing import TYPE_CHECKING

from utils.check_abc import STANDARD_SOURCE_ARGUMENTS, ManifestVsCatalogComparison
from utils.check_failure_messages import (
    manifest_vs_catalog_column_type_mismatch_message,
)

if TYPE_CHECKING:
    pass


class SourceColumnTypesMatchManifestVsCatalog(ManifestVsCatalogComparison):
    """Check if the source column types match between the manifest and the catalog.

    Attributes:
        manifest_items: dict of column names and types from the manifest
        catalog_items: dict of column names and types from the catalog
        check_name: name of the check
        additional_arguments: arguments required in addition to the global arguments
    """

    manifest_items: dict[str, str | None] = {}
    catalog_items: dict[str, str] = {}
    check_name: str = "source-column-types-match-manifest-vs-catalog"
    additional_arguments = STANDARD_SOURCE_ARGUMENTS

    def perform_check(self) -> None:
        """Execute the check logic."""
        eligible_columns = [
            column
            for column in self.manifest.in_scope_source_columns
            if getattr(column.parent, "enabled", True)
        ]
        eligible_sources: set[str] = {
            column.parent.unique_id for column in eligible_columns
        }
        self.manifest_items = {
            column.unique_id: column.data_type for column in eligible_columns
        }
        self.catalog_items = {
            column_id: column_data.type
            for source_id, source in self.catalog.sources.items()
            if source_id in eligible_sources
            for column_id, column_data in source.columns.items()
        }

    @property
    def failure_message(self) -> str:
        """Compile a failure log message."""
        return manifest_vs_catalog_column_type_mismatch_message(
            manifest_columns=self.manifest_items,
            catalog_columns=self.catalog_items,
        )
