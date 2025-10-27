"""Check if models have data tests."""

from utils.check_failure_messages import object_missing_attribute_message
from utils.check_abc import ManifestCheck
from utils.artifact_data import (
    get_models_from_manifest,
    get_json_artifact_data,
    MANIFEST_FILE_NAME,
)


class ModelsHaveDataTests(ManifestCheck):
    """Check if models have data tests.

    Attributes:
        check_name: name of the check
        additional_arguments: arguments required in addition to the global arguments
    """

    check_name: str = "models-have-data-tests"
    additional_arguments = [
        "data_tests",
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
        models = (
            node["unique_id"]
            for node in get_models_from_manifest(
                manifest_dir=self.args.manifest_dir,
                filter_conditions=self.filter_conditions,
            )
        )
        models_without_required_data_tests = set()
        data_tests: dict[str, set[str]] = {}
        manifest_data = get_json_artifact_data(
            self.args.manifest_dir / MANIFEST_FILE_NAME
        )
        for model in models:
            data_tests[model] = set()
            for child_id in manifest_data["child_map"][model]:
                node_data = manifest_data["nodes"].get(child_id, {})
                if node_data.get("resource_type") == "test":
                    test_name = node_data.get("test_metadata", {}).get("name")
                    if not self.args.data_tests or test_name in self.args.data_tests:
                        data_tests[model].add(test_name)
            if (
                self.args.data_tests and set(self.args.data_tests) - data_tests[model]
            ) or not data_tests[model]:
                models_without_required_data_tests.add(model)
        self.failures = models_without_required_data_tests

    @property
    def failure_message(self) -> str:
        """Compile a failure log message."""
        return object_missing_attribute_message(
            missing_attributes=self.failures,
            object_type="model",
            attribute_type="data test",
            expect_all_of_values=self.args.data_tests,
        )


if __name__ == "__main__":
    ModelsHaveDataTests()
