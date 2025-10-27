"""Check sources have data tests."""

from utils.check_failure_messages import object_missing_attribute_message
from utils.check_abc import ManifestCheck
from utils.artifact_data import (
    get_json_artifact_data,
    get_sources_from_manifest,
    MANIFEST_FILE_NAME,
)


class SourcesHaveDataTests(ManifestCheck):
    """Check sources have data tests.

    Attributes:
        check_name: name of the check
        additional_arguments: arguments required in addition to the global arguments
    """

    check_name: str = "sources-have-data-tests"
    additional_arguments = [
        "data_tests",
        "include_tags",
        "include_packages",
        "include_node_paths",
        "exclude_tags",
        "exclude_packages",
        "exclude_node_paths",
    ]

    def perform_check(self) -> None:
        """Execute the check logic."""
        sources = (
            node["unique_id"]
            for node in get_sources_from_manifest(
                manifest_dir=self.args.manifest_dir,
                filter_conditions=self.filter_conditions,
            )
        )
        sources_without_required_data_tests = set()
        data_tests: dict[str, set[str]] = {}
        manifest_data = get_json_artifact_data(
            self.args.manifest_dir / MANIFEST_FILE_NAME
        )
        for source in sources:
            data_tests[source] = set()
            for child_id in manifest_data["child_map"][source]:
                node_data = manifest_data["nodes"].get(child_id, {})
                if node_data.get("resource_type") == "test":
                    test_name = node_data.get("test_metadata", {}).get("name")
                    if not self.args.data_tests or test_name in self.args.data_tests:
                        data_tests[source].add(test_name)
            if (
                self.args.data_tests and set(self.args.data_tests) - data_tests[source]
            ) or not data_tests[source]:
                sources_without_required_data_tests.add(source)
        self.failures = sources_without_required_data_tests

    @property
    def failure_message(self) -> str:
        """Compile a failure log message."""
        return object_missing_attribute_message(
            missing_attributes=self.failures,
            object_type="source",
            attribute_type="data test",
            expect_all_of_values=self.args.data_tests,
        )


if __name__ == "__main__":
    SourcesHaveDataTests()
