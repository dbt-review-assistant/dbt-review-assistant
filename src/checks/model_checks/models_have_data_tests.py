"""Check if models have data tests."""

from utils.check_failure_messages import (
    object_missing_values_from_set_message,
)
from utils.check_abc import ManifestCheck


class ModelsHaveDataTests(ManifestCheck):
    """Check if models have data tests.

    Attributes:
        check_name: name of the check
        additional_arguments: arguments required in addition to the global arguments
    """

    check_name: str = "models-have-data-tests"
    additional_arguments = [
        "must_have_all_data_tests_from",
        "must_have_any_data_test_from",
        "include_materializations",
        "include_tags",
        "include_packages",
        "include_node_paths",
        "exclude_materializations",
        "exclude_tags",
        "exclude_packages",
        "exclude_node_paths",
    ]

    def perform_check(self) -> None:
        """Execute the check logic."""
        self.failures: dict[str, set[str]] = {
            model.unique_id: model.get_data_tests(self.manifest)
            for model in self.manifest.in_scope_models
            if not model.has_required_data_tests(
                data_tests=model.get_data_tests(self.manifest),
                must_have_all_data_tests_from=self.args.must_have_all_data_tests_from,
                must_have_any_data_test_from=self.args.must_have_any_data_test_from,
            )
        }

    @property
    def failure_message(self) -> str:
        """Compile a failure log message."""
        return object_missing_values_from_set_message(
            objects=self.failures,
            object_type="model",
            attribute_type="data test",
            must_have_all_from=self.args.must_have_all_data_tests_from,
            must_have_any_from=self.args.must_have_any_data_test_from,
        )


if __name__ == "__main__":
    ModelsHaveDataTests()
