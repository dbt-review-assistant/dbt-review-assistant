"""Check if the model column types match between the manifest and the catalog."""

from typing import TYPE_CHECKING

from utils.check_abc import STANDARD_MODEL_ARGUMENTS, ManifestVsCatalogComparison
from utils.check_failure_messages import (
    manifest_vs_catalog_column_type_mismatch_message,
)

if TYPE_CHECKING:
    from utils.manifest_object.manifest_object import ManifestColumn


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
        eligible_columns: list["ManifestColumn"] = [
            column
            for column in self.manifest.in_scope_model_columns
            if getattr(column.parent, "enabled", True)
            and getattr(column.parent, "materialized", "") != "ephemeral"
        ]
        eligible_models: set[str] = {
            column.parent.unique_id for column in eligible_columns
        }
        self.manifest_items = {
            column.unique_id: column.data_type for column in eligible_columns
        }
        self.catalog_items = {
            column_id: column.type
            for node_id, node in self.catalog.nodes.items()
            if node_id in eligible_models
            for column_id, column in node.columns.items()
        }

    @property
    def failure_message(self) -> str:
        """Compile a failure log message."""
        return manifest_vs_catalog_column_type_mismatch_message(
            manifest_columns=self.manifest_items,
            catalog_columns=self.catalog_items,
        )
