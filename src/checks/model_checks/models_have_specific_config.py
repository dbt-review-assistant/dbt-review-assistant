"""Check if models have a specific config."""

from typing import Any

from utils.check_abc import STANDARD_MODEL_ARGUMENTS, ManifestCheck
from utils.check_failure_messages import dictionary_values_mismatch
from utils.manifest_object.manifest_object import dict_difference


class ModelsHaveSpecificConfig(ManifestCheck):
    """Check if models have a specific config.

    Attributes:
        check_name: name of the check
        additional_arguments: arguments required in addition to the global arguments
    """

    check_name: str = "models-have-specific-config"
    additional_arguments = STANDARD_MODEL_ARGUMENTS + ["must_have_specific_config"]

    def perform_check(self) -> None:
        """Execute the check logic."""
        self.failures: dict[str, dict[str, Any]] = {
            model.unique_id: diff
            for model in self.manifest.in_scope_models
            if (
                diff := dict_difference(
                    model.config, self.args.must_have_specific_config
                )
            )
        }

    @property
    def failure_message(self) -> str:
        """Compile a failure log message."""
        return dictionary_values_mismatch(
            differences=self.failures,
            object_type="model",
            dict_name="config",
        )
