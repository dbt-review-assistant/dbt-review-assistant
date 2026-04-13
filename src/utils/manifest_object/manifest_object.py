"""Classes representing objects in the manifest file."""

import re
from abc import ABC
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Collection, Protocol, cast

from utils.manifest_object.node.model.constraint import Constraint

if TYPE_CHECKING:
    from utils.artifact_data import Manifest


class HasName(Protocol):
    """Protocol for objects implementing the name property."""

    @property
    def name(self) -> str:
        """The name of the object."""
        ...


class HasNameMixin(ABC):
    """Mixin for objects with name property."""

    def name_matches_regex(self, regex_pattern: str) -> bool:
        """Whether the object name matches a given regex pattern.

        Args:
            regex_pattern: the regex pattern to match against the object name.

        Returns:
            True if the object name matches a given regex pattern.
        """
        pattern = re.compile(regex_pattern)
        name = cast(HasName, self).name
        return bool(pattern.search(name))


@dataclass
class ManifestObject(HasNameMixin, ABC):
    """Abstract base class representing objects in the manifest file.

    Attributes:
        data: data for the object from the manifest file.
    """

    data: dict

    @property
    def description(self) -> str | None:
        """The object description."""
        return self.data.get("description")

    @property
    def unique_id(self) -> str:
        """The unique id of the object."""
        return self.data["unique_id"]

    @property
    def resource_type(self) -> str | None:
        """The resource type of the object."""
        return self.data.get("resource_type")

    @property
    def package_name(self) -> str | None:
        """The package name of the object."""
        return self.data.get("package_name")

    @property
    def name(self) -> str:
        """The name of the object."""
        return self.data["name"]

    @property
    def original_file_path(self) -> Path | None:
        """The original filepath of the object."""
        filepath = self.data.get("original_file_path")
        return Path(filepath) if filepath else None

    @property
    def meta(self) -> dict:
        """Meta dictionary of the object found in the manifest."""
        return self.data.get("meta", {})

    def is_included_by_original_or_patch_path(
        self, filepaths: Collection[Path]
    ) -> bool:
        """Whether this object should be included.

        Takes into consideration the original filepath, and also the patch path.
        If either are included in filepaths then it is included.

        Args:
            filepaths: Collection of Paths representing the files to include.

        Returns:
            True if the object should be included.
        """
        return (
            self.original_file_path in filepaths
            or getattr(self, "patch_path", None) in filepaths
        )


class HasData(Protocol):
    """Protocol for objects that have the data attribute."""

    data: dict[str, Any]


class HasPackageName(Protocol):
    """Protocol for objects that have the data attribute."""

    @property
    def package_name(self) -> str | None:
        """The package name of the object."""
        ...


class ConfigurableMixin(ABC):
    """Mixin for objects which can have config in the manifest."""

    @property
    def config(self) -> dict[str, Any]:
        """The config from the manifest."""
        return cast(HasData, self).data.get("config", {}) or {}

    @property
    def meta(self) -> dict[str, Any]:
        """Meta dictionary of the object found in the manifest."""
        if self.config.get("meta"):
            return self.config.get("meta", {})
        return cast(HasData, self).data.get("meta", {})

    @property
    def enabled(self) -> bool:
        """Whether the object is enabled in its config."""
        return self.config.get("enabled", True)


class HasPatchPathMixin(ABC, HasPackageName):
    """Mixin for objects which have the patch_path property."""

    @property
    def patch_path(self) -> Path | None:
        """The patch path from the manifest.

        This is the path to the associated properties.yml file.
        """
        data = cast(HasData, self).data
        path = data.get("patch_path")
        package_name = cast(HasPackageName, self).package_name
        if isinstance(path, str) and package_name and path.startswith(package_name):
            return Path(path.replace(f"{package_name}://", ""))
        return None


class TaggableMixin(ConfigurableMixin):
    """Mixin for objects which can be tagged."""

    @property
    def tags(self) -> set[str]:
        """All associated tags from the manifest."""
        config_tags = set(self.config.get("tags", []))
        manifest_tags = set(cast(HasData, self).data.get("tags", []))
        return config_tags.union(manifest_tags)

    def has_required_tags(
        self,
        must_have_all_tags_from: Collection[str] | None = None,
        must_have_any_tag_from: Collection[str] | None = None,
    ) -> bool:
        """Whether the object has the required tags.

        Args:
            must_have_all_tags_from: Collection of tags that the object must have. Optional, defaults to None
            must_have_any_tag_from: Collection of tags of which object must at least one. Optional, defaults to None
        """
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
    """Protocol for objects that have the unique_id property."""

    @property
    def unique_id(self) -> str:
        """The unique id of the object."""
        ...


@dataclass(eq=True, frozen=True)
class ManifestColumn(HasNameMixin):
    """Represents a column in the manifest file.

    Attributes:
        data: data for the column from the manifest file.
    """

    data: dict

    @property
    def name(self) -> str:
        """The name of the column."""
        return self.data["name"]

    @property
    def data_type(self) -> str | None:
        """The data type of the column."""
        return self.data.get("data_type")

    @property
    def has_data_type(self) -> bool:
        """Whether the object has the data type property."""
        return self.data_type is not None

    @property
    def description(self) -> str | None:
        """The column description."""
        return self.data.get("description")

    @property
    def has_description(self) -> bool:
        """Whether the object has a description."""
        return self.description is not None

    @property
    def constraints(self) -> tuple[Constraint, ...]:
        """Constraints for the column.

        Returns:
            a tuple of Constraints objects.
        """
        return tuple(
            Constraint(constraint_data)
            for constraint_data in self.data.get("constraints", [])
        )


class DataTestableMixin(ABC):
    """Mixin for objects which can have data tests in the manifest."""

    def get_data_tests(self, manifest: "Manifest") -> set[str]:
        """Get associated data tests for this object.

        Args:
            manifest: A Manifest instance to look up data tests from.

        Returns:
            set of data test IDs
        """
        unique_id = cast(HasUniqueId, self).unique_id
        generic_tests = {
            test.name
            for test in map(
                manifest.generic_tests.get, manifest.child_map.get(unique_id, [])
            )
            if test is not None and test.name is not None
        }
        singular_tests = {
            test.name
            for test in map(
                manifest.singular_tests.get, manifest.child_map.get(unique_id, [])
            )
            if test is not None
        }
        return generic_tests.union(singular_tests)

    def has_required_data_tests(
        self,
        manifest: "Manifest",
        must_have_all_data_tests_from: Collection[str] | None = None,
        must_have_any_data_test_from: Collection[str] | None = None,
    ) -> bool:
        """Whether the object has the required data tests.

        Args:
            manifest: Manifest instance to look up data tests from.
            must_have_all_data_tests_from: Collection of data test names that the object must have. Optional, defaults to None
            must_have_any_data_test_from: Collection of data test names from which object must have at least one. Optional, defaults to None

        Returns:
            Whether the object has the required data tests.
        """
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
    """Mixin for objects which can have columns."""

    @property
    def columns(self) -> dict[str, ManifestColumn]:
        """Columns associated with this object.

        Returns:
            a mapping of column unique IDs to ManifestColumn objects.
        """
        data = cast(HasData, self).data
        unique_id = cast(ManifestObject, self).unique_id
        return {
            f"{unique_id}.{column_name}": ManifestColumn(column_data)
            for column_name, column_data in data.get("columns", {}).items()
        }


class ManifestSource(
    DataTestableMixin, TaggableMixin, ManifestObject, HasPatchPathMixin, HasColumnsMixin
):
    """Represents a manifest source object."""

    pass


def dict_difference(
    left_dict: dict[str, Any], right_dict: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    """Get the difference between left_dict and right_dict.

    Only common keys are included in the comparison.

    Args:
        left_dict: dictionary representing the meta to compare.
        right_dict: dictionary representing the meta to compare.

    Returns:
        dictionary representing the difference in values.
    """
    return {
        key: {"this": left_dict.get(key), "other": value}
        for key, value in right_dict.items()
        if left_dict.get(key) != value
    }
