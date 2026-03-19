from abc import ABC
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, cast, TYPE_CHECKING
from utils.manifest_filter_conditions import ManifestFilterConditions
from utils.manifest_object.node.model.constraint import Constraint

if TYPE_CHECKING:
    from utils.artifact_data import Manifest


@dataclass(eq=True, frozen=True)
class ManifestObject(ABC):
    data: dict
    filter_conditions: ManifestFilterConditions

    @property
    def description(self) -> str | None:
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
    def is_in_scope(self) -> bool: ...


class HasFilterConditions(Protocol):
    filter_conditions: ManifestFilterConditions


class HasData(Protocol):
    data: dict[str, Any]


class ConfigurableMixin(ABC):
    @property
    def config(self) -> dict[str, Any]:
        return cast(HasData, self).data.get("config", {}) or {}

    @property
    def enabled(self) -> bool:
        return self.config.get("enabled", True)


class HasPatchPathMixin(ABC):
    @property
    def patch_path(self) -> Path | None:
        data = cast(HasData, self).data
        path = data.get("patch_path")
        if isinstance(path, str):
            return Path(path)
        return None


class TaggableMixin(ConfigurableMixin):
    @property
    def tags(self) -> set[str]:
        config_tags = set(self.config.get("tags", []))
        manifest_tags = set(cast(HasData, self).data.get("tags", []))
        return config_tags.union(manifest_tags)

    @property
    def filter_by_tags(self) -> bool:
        include_tags = cast(HasFilterConditions, self).filter_conditions.include_tags
        exclude_tags = cast(HasFilterConditions, self).filter_conditions.exclude_tags
        return (
            include_tags is None or bool(self.tags.intersection(include_tags))
        ) and (exclude_tags is None or not bool(self.tags.intersection(exclude_tags)))

    @property
    def is_in_scope(self) -> bool:
        return cast(ImplementsIsInScope, super()).is_in_scope and self.filter_by_tags

    def has_required_tags(
        self, must_have_all_tags_from=None, must_have_any_tag_from=None
    ) -> bool:
        has_required_tags = bool(self.tags)
        if must_have_all_tags_from is None and must_have_any_tag_from is None:
            return has_required_tags
        if must_have_all_tags_from is not None:
            has_required_tags = bool(set(must_have_all_tags_from).issubset(self.tags))
        if must_have_any_tag_from is not None:
            has_required_tags = (
                bool(set(must_have_any_tag_from).intersection(self.tags))
                and has_required_tags
            )
        return has_required_tags


class HasUniqueId(Protocol):
    @property
    def unique_id(self) -> str: ...


@dataclass(eq=True, frozen=True)
class ManifestColumn:
    data: dict

    @property
    def name(self) -> str:
        return self.data["name"]

    @property
    def data_type(self) -> str | None:
        return self.data.get("data_type")

    @property
    def has_data_type(self) -> bool:
        return self.data_type is not None

    @property
    def description(self) -> str | None:
        return self.data.get("description")

    @property
    def has_description(self) -> bool:
        return self.description is not None

    @property
    def constraints(self) -> tuple[Constraint, ...]:
        return tuple(
            Constraint(constraint_data)
            for constraint_data in self.data.get("constraints", [])
        )


class DataTestableMixin(ABC):
    def get_data_tests(self, manifest: "Manifest") -> set[str]:
        unique_id = cast(HasUniqueId, self).unique_id
        generic_tests = {
            test.generic_test_name
            for test in map(
                manifest.generic_tests.get, manifest.child_map.get(unique_id, [])
            )
            if test is not None and test.generic_test_name is not None
        }
        singular_tests = {
            test.unique_id
            for test in map(
                manifest.singular_tests.get, manifest.child_map.get(unique_id, [])
            )
            if test is not None
        }
        return generic_tests.union(singular_tests)

    def has_required_data_tests(
        self,
        manifest: "Manifest",
        must_have_all_data_tests_from,
        must_have_any_data_test_from,
    ) -> bool:
        data_tests = self.get_data_tests(manifest)
        has_required_data_tests = bool(data_tests)
        if (
            must_have_all_data_tests_from is None
            and must_have_any_data_test_from is None
        ):
            return has_required_data_tests
        if must_have_all_data_tests_from is not None:
            has_required_data_tests = bool(
                set(must_have_all_data_tests_from).issubset(data_tests)
            )
        if must_have_any_data_test_from is not None:
            has_required_data_tests = (
                bool(set(must_have_any_data_test_from).intersection(data_tests))
                and has_required_data_tests
            )
        return has_required_data_tests


class HasColumnsMixin(ABC):
    @property
    def columns(self) -> dict[str, ManifestColumn]:
        data = cast(HasData, self).data
        unique_id = cast(ManifestObject, self).unique_id
        return {
            f"{unique_id}.{column_name}": ManifestColumn(column_data)
            for column_name, column_data in data.get("columns", {}).items()
        }


class ManifestSource(
    DataTestableMixin, TaggableMixin, ManifestObject, HasPatchPathMixin, HasColumnsMixin
):
    pass
