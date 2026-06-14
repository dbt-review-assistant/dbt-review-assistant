"""Check if snapshot names match a regex pattern."""

from utils.check_abc import STANDARD_SNAPSHOT_ARGUMENTS, ManifestCheck
from utils.check_failure_messages import object_name_does_not_match_pattern


class SnapshotNamesMatchPattern(ManifestCheck):
    """Check if snapshot names match a regex pattern.

    Attributes:
        check_name: name of the check
        additional_arguments: arguments required in addition to the global arguments
    """

    check_name: str = "snapshot-names-match-pattern"
    additional_arguments = STANDARD_SNAPSHOT_ARGUMENTS + ["name_must_match_pattern"]

    def perform_check(self) -> None:
        """Execute the check logic."""
        self.failures = {
            snapshot.unique_id
            for snapshot in self.manifest.in_scope_snapshots
            if not snapshot.name_matches_regex(self.args.name_must_match_pattern)
        }

    @property
    def failure_message(self) -> str:
        """Compile a failure log message."""
        return object_name_does_not_match_pattern(
            objects=self.failures,
            object_type="snapshot",
            name_must_match_pattern=self.args.name_must_match_pattern,
        )
