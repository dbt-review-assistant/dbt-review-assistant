"""Check sources have data tests."""

from utils.check_abc import ManifestCheck
from utils.check_failure_messages import object_missing_values_from_set_message


class SourcesHaveDataTests(ManifestCheck):
    """Check sources have data tests.

    Attributes:
        check_name: name of the check
        additional_arguments: arguments required in addition to the global arguments
    """

    check_name: str = "sources-have-data-tests"
    additional_arguments = [
        "must_have_all_data_tests_from",
        "must_have_any_data_test_from",
        "include_tags",
        "include_packages",
        "include_node_paths",
        "exclude_tags",
        "exclude_packages",
        "exclude_node_paths",
    ]

    def perform_check(self) -> None:
        """Execute the check logic."""
        self.failures: dict[str, set[str]] = {
            source.unique_id: source.get_data_tests(self.manifest)
            for source in self.manifest.in_scope_sources
            if not source.has_required_data_tests(
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
            object_type="source",
            attribute_type="data test",
            must_have_all_from=self.args.must_have_all_data_tests_from,
            must_have_any_from=self.args.must_have_any_data_test_from,
        )
