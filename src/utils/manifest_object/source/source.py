from functools import lru_cache
from typing import Any, TYPE_CHECKING

from utils.manifest_object.manifest_object import ManifestObject
from utils.manifest_object.source.column import ManifestSourceColumn

if TYPE_CHECKING:
    from utils.artifact_data import Manifest


class ManifestSource(ManifestObject):
    def filter_by_resource_type(self) -> bool:
        return self.data.get("resource_type") == "source"

    @property
    def patch_path(self) -> str:
        return self.data["patch_path"]

    @property
    def config(self) -> dict[str, Any]:
        return self.data.get("config", {})

    @property
    def enabled(self) -> bool:
        return self.config.get("enabled", True)

    @property
    def tags(self) -> set[str]:
        manifest_tags = self.data.get("tags", [])
        if isinstance(manifest_tags, str):
            manifest_tags = [manifest_tags]
        config_tags = self.config.get("tags", [])
        if isinstance(config_tags, str):
            config_tags = [config_tags]
        return set(manifest_tags + config_tags)

    def filter_by_tag(self) -> bool:
        return (
            self.filter_conditions.include_tags is None
            or self.tags.intersection(set(self.filter_conditions.include_tags))
        ) and (
            self.filter_conditions.exclude_tags is None
            or not self.tags.intersection(set(self.filter_conditions.exclude_tags))
        )

    @property
    def is_in_scope(self) -> bool:
        return all(
            [
                super().is_in_scope,
                self.filter_by_tag(),
            ]
        )

    @lru_cache
    def get_data_tests(self, manifest: "Manifest") -> set[str]:
        return {
            test.generic_test_name
            for test in map(
                manifest.get_generic_test, manifest.child_map.get(self.unique_id, [])
            )
            if test
        }

    @staticmethod
    def has_required_data_tests(
        data_tests: set[str],
        must_have_all_data_tests_from,
        must_have_any_data_test_from,
    ) -> bool:
        return not any(
            [
                # No specific data_tests required
                # TODO - accept singular tests here too
                (
                    not (must_have_all_data_tests_from or must_have_any_data_test_from)
                    and not data_tests
                ),
                # Full set of data_tests required
                (
                    must_have_all_data_tests_from
                    and not set(must_have_all_data_tests_from).issubset(data_tests)
                ),
                # At least one data_test from set required
                (
                    must_have_any_data_test_from
                    and not set(must_have_any_data_test_from).intersection(data_tests)
                ),
            ]
        )

    @property
    def columns(self) -> dict[str, ManifestSourceColumn]:
        return {
            f"{self.unique_id}.{column_name}": ManifestSourceColumn(column_data)
            for column_name, column_data in self.data.get("columns", {}).items()
        }
