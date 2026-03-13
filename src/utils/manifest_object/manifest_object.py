from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, cast

from utils.manifest_filter_conditions import ManifestFilterConditions


@dataclass(eq=True, frozen=True)
class ManifestObject(ABC):
    data: dict
    filter_conditions: ManifestFilterConditions

    @property
    def description(self) -> str:
        return self.data.get("description")

    @property
    def unique_id(self) -> str:
        return self.data["unique_id"]

    @property
    def resource_type(self) -> str | None:
        return self.data.get("resource_type")

    @property
    def package_name(self) -> str | None:
        return self.data.get("package_name")

    @property
    def filter_by_package(self) -> bool:
        return (
            self.filter_conditions.include_packages is None
            or self.package_name in self.filter_conditions.include_packages
        ) and (
            self.filter_conditions.exclude_packages is None
            or self.package_name not in self.filter_conditions.exclude_packages
        )

    @property
    def filter_by_path(self) -> bool:
        return (
            self.filter_conditions.include_paths is None
            or any(
                Path(self.data["original_file_path"]).is_relative_to(path)
                for path in self.filter_conditions.include_paths
            )
        ) and (
            self.filter_conditions.exclude_paths is None
            or not any(
                Path(self.data["original_file_path"]).is_relative_to(path)
                for path in self.filter_conditions.exclude_paths
            )
        )

    @property
    def filter_by_resource_type(self) -> bool:
        return (
            self.filter_conditions.include_resource_types is None
            or self.resource_type in self.filter_conditions.include_resource_types
        ) and (
            self.filter_conditions.exclude_resource_types is None
            or self.resource_type not in self.filter_conditions.exclude_resource_types
        )

    @property
    def is_in_scope(self) -> bool:
        return all(
            [
                self.filter_by_resource_type,
                self.filter_by_package,
                self.filter_by_path,
            ]
        )

class ImplementsIsInScope(Protocol):
    @property
    def is_in_scope(self) -> bool:
        ...


class HasFilterConditions(Protocol):
    filter_conditions: ManifestFilterConditions


class HasData(Protocol):
    data: dict[str, Any]

class ConfigurableMixin(ABC):
    @property
    def config(self) -> dict[str, Any]:
        return cast(HasData, self).data.get("config", {}) or {}


class HasPatchPathMixin(ABC):
    @property
    def patch_path(self) -> Path:
        return Path(cast(HasData, self).data["patch_path"])


class TaggableMixin(ConfigurableMixin):
    @property
    def tags(self) -> set[str]:
        config_tags = self.config.get("tags", [])
        if isinstance(config_tags, str):
            config_tags = [config_tags]
        manifest_tags = cast(HasData, self).data.get("tags", [])
        if isinstance(manifest_tags, str):
            manifest_tags = [manifest_tags]
        return set(config_tags).union(manifest_tags)

    @property
    def filter_by_tags(self) -> bool:
        return (
            cast(HasFilterConditions, self).filter_conditions.include_tags is None
            or bool(self.tags.intersection(set(cast(HasFilterConditions, self).filter_conditions.include_tags)))
        ) and (
            cast(HasFilterConditions, self).filter_conditions.exclude_tags is None
            or not bool(self.tags.intersection(set(cast(HasFilterConditions, self).filter_conditions.exclude_tags)))
        )

    @property
    def is_in_scope(self) -> bool:
        return cast(ImplementsIsInScope, super()).is_in_scope and self.filter_by_tags

    def has_required_tags(
        self, must_have_all_tags_from=None, must_have_any_tag_from=None
    ) -> bool:
        has_required_tags = bool(self.tags)
        if (
            must_have_all_tags_from is None
            and must_have_any_tag_from is None
        ):
            return has_required_tags
        if must_have_all_tags_from is not None:
            has_required_tags = bool(
                set(must_have_all_tags_from).issubset(self.tags)
            )
        if must_have_any_tag_from is not None:
            has_required_tags = (
                bool(set(must_have_any_tag_from).intersection(self.tags))
                and has_required_tags
            )
        return has_required_tags
