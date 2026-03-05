from abc import ABC
from typing import Any

from utils.manifest_object.node.model.column import Constraint
from utils.manifest_object.manifest_object import ManifestObject


class ManifestNode(ManifestObject, ABC):
    @property
    def enabled(self) -> bool:
        return self.config.get("enabled", True)

    @property
    def constraints(self) -> tuple[Constraint, ...]:
        return tuple(
            Constraint(constraint_data)
            for constraint_data in self.data.get("constraints", [])
        )

    @property
    def patch_path(self) -> str | None:
        return self.data.get("patch_path")

    @property
    def config(self) -> dict[str, Any]:
        return self.data.get("config", {})

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
