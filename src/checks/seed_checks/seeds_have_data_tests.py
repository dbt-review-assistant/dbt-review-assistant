"""Check if seeds have data tests."""

from utils.check_abc import STANDARD_SEED_ARGUMENTS, ManifestCheck
from utils.check_failure_messages import object_missing_values_from_set_message


class SeedsHaveDataTests(ManifestCheck):
    """Check if seeds have data tests.

    Attributes:
        check_name: name of the check
        additional_arguments: arguments required in addition to the global arguments
    """

    check_name: str = "seeds-have-data-tests"
    additional_arguments = STANDARD_SEED_ARGUMENTS + [
        "must_have_all_data_tests_from",
        "must_have_any_data_test_from",
    ]

    def perform_check(self) -> None:
        """Execute the check logic."""
        self.failures: dict[str, set[str]] = {
            seed.unique_id: seed.get_data_tests(self.manifest)
            for seed in self.manifest.in_scope_seeds
            if not seed.has_required_data_tests(
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
            object_type="seed",
            attribute_type="data test",
            must_have_all_from=self.args.must_have_all_data_tests_from,
            must_have_any_from=self.args.must_have_any_data_test_from,
        )
