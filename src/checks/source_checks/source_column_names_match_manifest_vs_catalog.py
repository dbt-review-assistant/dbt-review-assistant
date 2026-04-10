"""Check if the source column names match between the manifest and the catalog."""

from utils.check_abc import STANDARD_SOURCE_ARGUMENTS, ManifestVsCatalogComparison
from utils.check_failure_messages import (
    manifest_vs_catalog_column_name_mismatch_message,
)


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
        eligible_sources = {
            source.unique_id: source
            for source in self.manifest.in_scope_sources
            if source.enabled
        }
        self.manifest_items = {
            column_id
            for node_name, node in eligible_sources.items()
            for column_id in node.columns.keys()
        }
        self.catalog_items = {
            column_id
            for source_id, source in self.catalog.sources.items()
            if source_id in eligible_sources.keys()
            for column_id in source.columns.keys()
        }

    @property
    def failure_message(self) -> str:
        """Compile a failure log message."""
        return manifest_vs_catalog_column_name_mismatch_message(
            manifest_columns=self.manifest_items,
            catalog_columns=self.catalog_items,
        )
