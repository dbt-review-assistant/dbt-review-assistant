"""Check if the source column names match between the manifest and the catalog."""

from typing import TYPE_CHECKING

from utils.check_abc import STANDARD_SOURCE_ARGUMENTS, ManifestVsCatalogComparison
from utils.check_failure_messages import (
    manifest_vs_catalog_column_name_mismatch_message,
)

if TYPE_CHECKING:
    from utils.manifest_object.manifest_object import ManifestColumn


class SourceColumnNamesMatchManifestVsCatalog(ManifestVsCatalogComparison):
    """Check if the source column names match between the manifest and the catalog.

    Attributes:
        manifest_items: set of column names from the manifest
        catalog_items: set of column names from the catalog
        check_name: name of the check
        additional_arguments: arguments required in addition to the global arguments
    """

    manifest_items: set[str] = set()
    catalog_items: set[str] = set()
    check_name: str = "source-column-names-match-manifest-vs-catalog"
    additional_arguments = STANDARD_SOURCE_ARGUMENTS

    def perform_check(self) -> None:
        """Execute the check logic."""
        eligible_columns: list["ManifestColumn"] = [
            column
            for column in self.manifest.in_scope_source_columns
            if getattr(column.parent, "enabled", True)
        ]
        eligible_sources: set[str] = {
            column.parent.unique_id for column in eligible_columns
        }
        self.manifest_items = {column.unique_id for column in eligible_columns}
        self.catalog_items = {
            column_id
            for source_id, source in self.catalog.sources.items()
            if source_id in eligible_sources
            for column_id in source.columns.keys()
        }

    @property
    def failure_message(self) -> str:
        """Compile a failure log message."""
        return manifest_vs_catalog_column_name_mismatch_message(
            manifest_columns=self.manifest_items,
            catalog_columns=self.catalog_items,
        )
