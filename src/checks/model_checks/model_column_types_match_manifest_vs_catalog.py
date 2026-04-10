"""Check if the model column types match between the manifest and the catalog."""

from utils.check_abc import STANDARD_MODEL_ARGUMENTS, ManifestVsCatalogComparison
from utils.check_failure_messages import (
    manifest_vs_catalog_column_type_mismatch_message,
)


class ModelColumnTypesMatchManifestVsCatalog(ManifestVsCatalogComparison):
    """Check if the model column types match between the manifest and the catalog.

    Attributes:
        manifest_items: dict of column names and types from the manifest
        catalog_items: dict of column names and types from the catalog
        check_name: name of the check
        additional_arguments: arguments required in addition to the global arguments
    """

    manifest_items: dict[str, str | None] = {}
    catalog_items: dict[str, str] = {}
    check_name: str = "model-column-types-match-manifest-vs-catalog"
    additional_arguments = STANDARD_MODEL_ARGUMENTS

    def perform_check(self) -> None:
        """Execute the check logic."""
        eligible_models = {
            model.unique_id: model
            for model in self.manifest.in_scope_models
            if model.enabled and model.materialized != "ephemeral"
        }
        self.manifest_items = {
            column_id: column.data_type
            for model in eligible_models.values()
            for column_id, column in model.columns.items()
        }
        self.catalog_items = {
            column_id: column.type
            for node_id, node in self.catalog.nodes.items()
            if node_id in eligible_models.keys()
            for column_id, column in node.columns.items()
        }

    @property
    def failure_message(self) -> str:
        """Compile a failure log message."""
        return manifest_vs_catalog_column_type_mismatch_message(
            manifest_columns=self.manifest_items,
            catalog_columns=self.catalog_items,
        )
