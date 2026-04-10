"""Check if model columns have types."""

from utils.check_abc import STANDARD_MODEL_ARGUMENTS, ManifestCheck
from utils.check_failure_messages import object_missing_attribute_message


class ModelColumnsHaveTypes(ManifestCheck):
    """Check if model columns have types.

    Attributes:
        check_name: name of the check
        additional_arguments: arguments required in addition to the global arguments
    """

    check_name: str = "model-columns-have-types"
    additional_arguments = STANDARD_MODEL_ARGUMENTS

    def perform_check(self) -> None:
        """Execute the check logic."""
        self.failures: set[str] = {
            column_id
            for model in self.manifest.in_scope_models
            for column_id, column in model.columns.items()
            if not column.has_data_type
        }

    @property
    def failure_message(self) -> str:
        """Compile a failure log message."""
        return object_missing_attribute_message(
            missing_attributes=self.failures,
            object_type="model column",
            attribute_type="data_type",
        )
