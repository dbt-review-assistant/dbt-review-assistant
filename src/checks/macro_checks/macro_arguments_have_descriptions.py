"""Check if macro arguments have descriptions."""

from utils.check_failure_messages import object_missing_attribute_message
from utils.check_abc import ManifestCheck


class MacroArgumentsHaveDescriptions(ManifestCheck):
    """Check if macro arguments have descriptions.

    Attributes:
        check_name: name of the check
        additional_arguments: arguments required in addition to the global arguments
    """

    check_name: str = "macro-arguments-have-descriptions"
    additional_arguments = [
        "include_packages",
        "include_tags",
        "exclude_packages",
        "exclude_tags",
    ]

    def perform_check(self) -> None:
        """Execute the check logic."""
        self.failures = {
            f"{macro.unique_id}.{argument.name}"
            for macro in self.manifest.in_scope_macros
            for argument in macro.arguments
            if not argument.description
        }

    @property
    def failure_message(self) -> str:
        """Compile a failure log message."""
        return object_missing_attribute_message(
            missing_attributes=self.failures,
            object_type="macro argument",
            attribute_type="description",
        )
