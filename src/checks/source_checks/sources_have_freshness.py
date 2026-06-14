"""Check sources have freshness configured."""

from utils.check_abc import STANDARD_SOURCE_ARGUMENTS, ManifestCheck
from utils.check_failure_messages import object_missing_attribute_message


class SourcesHaveFreshness(ManifestCheck):
    """Check sources have freshness configured.

    Attributes:
        check_name: name of the check
        additional_arguments: arguments required in addition to the global arguments
    """

    check_name: str = "sources-have-freshness"
    additional_arguments = STANDARD_SOURCE_ARGUMENTS

    def perform_check(self) -> None:
        """Execute the check logic."""
        self.failures = {
            source.unique_id
            for source in self.manifest.in_scope_sources
            if not source.has_freshness
        }

    @property
    def failure_message(self) -> str:
        """Compile a failure log message."""
        return object_missing_attribute_message(
            missing_attributes=self.failures,
            object_type="source",
            attribute_type="freshness",
        )
