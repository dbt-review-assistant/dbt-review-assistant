"""Check if models are materialized with one of a set of allowed materializations."""

from utils.check_abc import STANDARD_MODEL_ARGUMENTS, ManifestCheck
from utils.check_failure_messages import (
    object_attribute_value_not_in_set,
)


class ModelsHaveSpecificMaterialization(ManifestCheck):
    """Check if models are materialized with one of a set of allowed materializations.

    Attributes:
        check_name: name of the check
        additional_arguments: arguments required in addition to the global arguments
    """

    failures: dict[str, str | None]
    check_name: str = "models-have-specific-materialization"
    additional_arguments = STANDARD_MODEL_ARGUMENTS + ["must_be_materialized_as_one_of"]

    def perform_check(self) -> None:
        """Execute the check logic."""
        self.failures = {
            model.unique_id: model.materialized
            for model in self.manifest.in_scope_models
            if model.materialized not in set(self.args.must_be_materialized_as_one_of)
        }

    @property
    def failure_message(self) -> str:
        """Compile a failure log message."""
        return object_attribute_value_not_in_set(
            objects=self.failures,
            object_type="model",
            attribute_type="materialization",
            allowed_values=self.args.must_be_materialized_as_one_of,
        )
