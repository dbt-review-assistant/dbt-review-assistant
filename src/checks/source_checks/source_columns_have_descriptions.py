"""Check if source columns have descriptions."""

from utils.check_abc import STANDARD_SOURCE_ARGUMENTS, ManifestCheck
from utils.check_failure_messages import object_missing_attribute_message


class SourceColumnsHaveDescriptions(ManifestCheck):
    """Check if source columns have descriptions.

    Attributes:
        check_name: name of the check
        additional_arguments: arguments required in addition to the global arguments
    """

    check_name: str = "source-columns-have-descriptions"
    additional_arguments = STANDARD_SOURCE_ARGUMENTS

    def perform_check(self) -> None:
        """Execute the check logic."""
        self.failures = {
            column.unique_id
            for column in self.manifest.in_scope_source_columns
            if not column.description
        }

    @property
    def failure_message(self) -> str:
        """Compile a failure log message."""
        return object_missing_attribute_message(
            missing_attributes=self.failures,
            object_type="source column",
            attribute_type="description",
        )
