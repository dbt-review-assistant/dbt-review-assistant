"""CHeck if models have a description."""

from utils.check_abc import ManifestCheck
from utils.check_failure_messages import object_name_does_not_match_pattern


class MacroNamesMatchPattern(ManifestCheck):
    """Check if macro names match a regex pattern.

    Attributes:
        check_name: name of the check
        additional_arguments: arguments required in addition to the global arguments
    """

    check_name: str = "macro-names-match-pattern"
    additional_arguments = [
        "include_tags",
        "include_packages",
        "exclude_tags",
        "exclude_packages",
        "name_must_match_pattern",
    ]

    def perform_check(self) -> None:
        """Execute the check logic."""
        self.failures = {
            macro.unique_id
            for macro in self.manifest.in_scope_macros
            if not macro.name_matches_regex(self.args.name_must_match_pattern)
        }

    @property
    def failure_message(self) -> str:
        """Compile a failure log message."""
        return object_name_does_not_match_pattern(
            objects=self.failures,
            object_type="macro",
            name_must_match_pattern=self.args.name_must_match_pattern,
        )
