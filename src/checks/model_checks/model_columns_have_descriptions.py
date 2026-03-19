"""Check if model columns have descriptions."""

from utils.check_abc import ManifestCheck
from utils.check_failure_messages import object_missing_attribute_message


class ModelColumnsHaveDescriptions(ManifestCheck):
    """Check if model columns have descriptions.

    Attributes:
        check_name: name of the check
        additional_arguments: arguments required in addition to the global arguments
    """

    check_name: str = "model-columns-have-descriptions"
    additional_arguments = [
        "include_materializations",
        "include_tags",
        "include_packages",
        "include_node_paths",
        "exclude_materializations",
        "exclude_tags",
        "exclude_packages",
        "exclude_node_paths",
    ]

    def perform_check(self) -> None:
        """Execute the check logic."""
        self.failures = {
            column_id
            for model in self.manifest.in_scope_models
            for column_id, column in model.columns.items()
            if not column.description
        }

    @property
    def failure_message(self) -> str:
        """Compile a failure log message."""
        return object_missing_attribute_message(
            missing_attributes=self.failures,
            object_type="model column",
            attribute_type="description",
        )
