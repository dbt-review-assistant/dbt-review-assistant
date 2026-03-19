"""CHeck if models have a description."""

from utils.check_abc import ManifestCheck
from utils.check_failure_messages import object_name_does_not_match_pattern


class ModelColumnNamesMatchPattern(ManifestCheck):
    """Check if model names match a regex pattern.

    Attributes:
        check_name: name of the check
        additional_arguments: arguments required in addition to the global arguments
    """

    check_name: str = "model-column-names-match-pattern"
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
        "name_must_match_pattern",
    ]

    def perform_check(self) -> None:
        """Execute the check logic."""
        self.failures = {
            column_id
            for model in self.manifest.in_scope_models
            for column_id, column in model.columns.items()
            if not column.name_matches_regex(self.args.name_must_match_pattern)
        }

    @property
    def failure_message(self) -> str:
        """Compile a failure log message."""
        return object_name_does_not_match_pattern(
            objects=self.failures,
            object_type="model column",
            name_must_match_pattern=self.args.name_must_match_pattern,
        )
