from typing import Any

from utils.manifest_object.manifest_object import ManifestObject


class UnitTest(ManifestObject):
    def filter_by_resource_type(self) -> bool:
        return self.data.get("resource_type") == "unit_test"

    @property
    def original_filepath(self) -> str:
        return self.data["original_filepath"]

    @property
    def patch_path(self) -> str:
        return self.data["patch_path"]

    @property
    def config(self) -> dict[str, Any]:
        return self.data.get("config", {})

    @property
    def tags(self) -> set[str]:
        config_tags = self.config.get("tags", [])
        if isinstance(config_tags, str):
            config_tags = [config_tags]
        return set(config_tags)

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
