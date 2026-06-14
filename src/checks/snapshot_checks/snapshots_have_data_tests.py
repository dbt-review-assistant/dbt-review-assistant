"""Check if snapshots have data tests."""

from utils.check_abc import STANDARD_SNAPSHOT_ARGUMENTS, ManifestCheck
from utils.check_failure_messages import object_missing_values_from_set_message


class SnapshotsHaveDataTests(ManifestCheck):
    """Check if snapshots have data tests.

    Attributes:
        check_name: name of the check
        additional_arguments: arguments required in addition to the global arguments
    """

    check_name: str = "snapshots-have-data-tests"
    additional_arguments = STANDARD_SNAPSHOT_ARGUMENTS + [
        "must_have_all_data_tests_from",
        "must_have_any_data_test_from",
    ]

    def perform_check(self) -> None:
        """Execute the check logic."""
        self.failures: dict[str, set[str]] = {
            snapshot.unique_id: snapshot.get_data_tests(self.manifest)
            for snapshot in self.manifest.in_scope_snapshots
            if not snapshot.has_required_data_tests(
                manifest=self.manifest,
                must_have_all_data_tests_from=self.args.must_have_all_data_tests_from,
                must_have_any_data_test_from=self.args.must_have_any_data_test_from,
            )
        }

    @property
    def failure_message(self) -> str:
        """Compile a failure log message."""
        return object_missing_values_from_set_message(
            objects=self.failures,
            object_type="snapshot",
            attribute_type="data test",
            must_have_all_from=self.args.must_have_all_data_tests_from,
            must_have_any_from=self.args.must_have_any_data_test_from,
        )
