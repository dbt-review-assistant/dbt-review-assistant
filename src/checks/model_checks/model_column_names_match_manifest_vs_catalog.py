"""Check if the model column names match between the manifest and the catalog."""

from utils.check_abc import ManifestVsCatalogComparison
from utils.check_failure_messages import (
    manifest_vs_catalog_column_name_mismatch_message,
)


class ModelColumnNamesMatchManifestVsCatalog(ManifestVsCatalogComparison):
    """Check if the model column names match between the manifest and the catalog.

    Attributes:
        manifest_items: set of column names from the manifest
        catalog_items: set of column names from the catalog
        check_name: name of the check
        additional_arguments: arguments required in addition to the global arguments
    """

    manifest_items: set[str] = set()
    catalog_items: set[str] = set()
    check_name: str = "model-column-names-match-manifest-vs-catalog"
    additional_arguments = [
        "include_materializations",
        "include_tags",
        "include_packages",
        "include_node_paths",
        "include_name_patterns",
        "exclude_materializations",
        "exclude_tags",
        "exclude_packages",
        "exclude_node_paths",
        "exclude_name_patterns",
    ]

    def perform_check(self) -> None:
        """Execute the check logic."""
        eligible_models = {
            model.unique_id: model
            for model in self.manifest.in_scope_models
            if model.enabled
        }
        self.manifest_items: set[str] = {
            column_id
            for model in eligible_models.values()
            for column_id, column in model.columns.items()
        }
        self.catalog_items = {
            column_id
            for node_id, node in self.catalog.nodes.items()
            if node_id in eligible_models.keys()
            for column_id in node.columns.keys()
        }

    @property
    def failure_message(self) -> str:
        """Compile a failure log message."""
        return manifest_vs_catalog_column_name_mismatch_message(
            manifest_columns=self.manifest_items,
            catalog_columns=self.catalog_items,
        )
