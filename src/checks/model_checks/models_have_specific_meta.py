"""Check if models have a specific meta."""

from typing import Any

from utils.check_abc import STANDARD_MODEL_ARGUMENTS, ManifestCheck
from utils.check_failure_messages import dictionary_values_mismatch
from utils.manifest_object.manifest_object import dict_difference


class ModelsHaveSpecificMeta(ManifestCheck):
    """Check if models have a specific meta.

    Attributes:
        check_name: name of the check
        additional_arguments: arguments required in addition to the global arguments
    """

    check_name: str = "models-have-specific-meta"
    additional_arguments = STANDARD_MODEL_ARGUMENTS + ["must_have_specific_meta"]

    def perform_check(self) -> None:
        """Execute the check logic."""
        self.failures: dict[str, dict[str, Any]] = {
            model.unique_id: dict_difference(
                model.meta, self.args.must_have_specific_meta
            )
            for model in self.manifest.in_scope_models
            if dict_difference(model.meta, self.args.must_have_specific_meta)
        }

    @property
    def failure_message(self) -> str:
        """Compile a failure log message."""
        return dictionary_values_mismatch(
            differences=self.failures,
            object_type="model",
            dict_name="meta",
        )
