"""Check if models have an access level configured."""

from utils.check_abc import STANDARD_MODEL_ARGUMENTS, ManifestCheck
from utils.check_failure_messages import object_attribute_value_not_in_set


class ModelsHaveAccess(ManifestCheck):
    """Check if models have an access level configured.

    Attributes:
        check_name: name of the check
        additional_arguments: arguments required in addition to the global arguments
        failures: dict mapping unique IDs to their current access value
    """

    failures: dict[str, str | None]
    check_name: str = "models-have-access"
    additional_arguments = STANDARD_MODEL_ARGUMENTS + ["must_be_accessed_as_one_of"]

    def perform_check(self) -> None:
        """Execute the check logic."""
        self.failures = {
            model.unique_id: model.access
            for model in self.manifest.in_scope_models
            if model.access not in set(self.args.must_be_accessed_as_one_of)
        }

    @property
    def failure_message(self) -> str:
        """Compile a failure log message."""
        return object_attribute_value_not_in_set(
            objects=self.failures,
            object_type="model",
            attribute_type="access",
            allowed_values=self.args.must_be_accessed_as_one_of,
        )
