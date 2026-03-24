"""Check sources have columns listed in the manifest."""

from utils.check_abc import ManifestCheck
from utils.check_failure_messages import object_missing_attribute_message


class SourcesHaveColumns(ManifestCheck):
    """Check sources have columns listed in the manifest.

    Attributes:
        check_name: name of the check
        additional_arguments: arguments required in addition to the global arguments
    """

    check_name: str = "sources-have-columns"
    additional_arguments = [
        "include_tags",
        "include_packages",
        "include_node_paths",
        "include_name_patterns",
        "exclude_tags",
        "exclude_packages",
        "exclude_node_paths",
        "exclude_name_patterns",
    ]

    def perform_check(self) -> None:
        """Execute the check logic."""
        self.failures = {
            source.unique_id
            for source in self.manifest.in_scope_sources
            if not source.columns
        }

    @property
    def failure_message(self) -> str:
        """Compile a failure log message."""
        return object_missing_attribute_message(
            missing_attributes=self.failures,
            object_type="source",
            attribute_type="column",
        )
