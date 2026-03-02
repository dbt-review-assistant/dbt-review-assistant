from abc import ABC
from pathlib import Path

from utils.manifest_filter_conditions import ManifestFilterConditions


class ManifestObject(ABC):
    def __init__(
        self, data: dict, filter_conditions: "ManifestFilterConditions"
    ) -> None:
        self.data = data
        self.filter_conditions = filter_conditions

    def __eq__(self, other: "ManifestObject") -> bool:
        return (
            type(self) is type(other)
            and self.data == other.data
            and self.filter_conditions == other.filter_conditions
        )

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
