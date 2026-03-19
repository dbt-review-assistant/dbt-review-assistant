"""Check macros have descriptions."""

from utils.check_failure_messages import object_missing_attribute_message
from utils.check_abc import ManifestCheck


class MacrosHaveDescriptions(ManifestCheck):
    """Check macros have descriptions.

    Attributes:
        check_name: name of the check
        additional_arguments: arguments required in addition to the global arguments
    """

    check_name: str = "macros-have-descriptions"
    additional_arguments = [
        "include_packages",
        "include_tags",
        "exclude_packages",
        "exclude_tags",
    ]

    def perform_check(self) -> None:
        """Execute the check logic."""
        self.failures = {
            macro.unique_id
            for macro in self.manifest.in_scope_macros
            if not macro.description
        }

    @property
    def failure_message(self) -> str:
        """Compile a failure log message."""
        return object_missing_attribute_message(
            missing_attributes=self.failures,
            object_type="macro",
            attribute_type="description",
        )
