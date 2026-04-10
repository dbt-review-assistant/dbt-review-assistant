"""Check if model names match a regex pattern."""

from utils.check_abc import STANDARD_MODEL_ARGUMENTS, ManifestCheck
from utils.check_failure_messages import object_name_does_not_match_pattern


class ModelNamesMatchPattern(ManifestCheck):
    """Check if model names match a regex pattern.

    Attributes:
        check_name: name of the check
        additional_arguments: arguments required in addition to the global arguments
    """

    check_name: str = "model-names-match-pattern"
    additional_arguments = STANDARD_MODEL_ARGUMENTS + ["name_must_match_pattern"]

    def perform_check(self) -> None:
        """Execute the check logic."""
        self.failures = {
            model.unique_id
            for model in self.manifest.in_scope_models
            if not model.name_matches_regex(self.args.name_must_match_pattern)
        }

    @property
    def failure_message(self) -> str:
        """Compile a failure log message."""
        return object_name_does_not_match_pattern(
            objects=self.failures,
            object_type="model",
            name_must_match_pattern=self.args.name_must_match_pattern,
        )
