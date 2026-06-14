"""Check snapshots have descriptions."""

from utils.check_abc import STANDARD_SNAPSHOT_ARGUMENTS, ManifestCheck
from utils.check_failure_messages import object_missing_attribute_message


class SnapshotsHaveDescriptions(ManifestCheck):
    """Check snapshots have descriptions.

    Attributes:
        check_name: name of the check
        additional_arguments: arguments required in addition to the global arguments
    """

    check_name: str = "snapshots-have-descriptions"
    additional_arguments = STANDARD_SNAPSHOT_ARGUMENTS

    def perform_check(self) -> None:
        """Execute the check logic."""
        self.failures = {
            snapshot.unique_id
            for snapshot in self.manifest.in_scope_snapshots
            if not snapshot.description
        }

    @property
    def failure_message(self) -> str:
        """Compile a failure log message."""
        return object_missing_attribute_message(
            missing_attributes=self.failures,
            object_type="snapshot",
            attribute_type="description",
        )
