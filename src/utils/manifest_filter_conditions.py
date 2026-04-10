"""Class for filtering manifest objects."""

from abc import ABC, abstractmethod
from argparse import Namespace
from dataclasses import InitVar, dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Collection, Optional

from utils.console_formatting import ConsoleEmphasis, colour_message
from utils.get_relatives import (
    get_all_children,
    get_all_parents,
    get_direct_children,
    get_direct_parents,
)

if TYPE_CHECKING:
    from utils.artifact_data import Manifest
    from utils.manifest_object.manifest_object import (
        ManifestObject,
    )


@dataclass(eq=True)
class ManifestFilterMethod(ABC):
    """Abstract base class for methods for filtering manifest objects.

    Attributes:
        include_values: set of values which indicate an object should be included.
        exclude_values: set of values which indicate an object should be excluded.
    """

    args: InitVar[Namespace | None] = None
    include_values: set[Any] | None = None
    exclude_values: set[Any] | None = None

    def __post_init__(
        self,
        args: Namespace | None,
    ) -> None:
        """Initialize the instance.

        Args:
            args: CLI args Namespace instance passed to the constructor.
        """
        _include_values = self.get_values_from_args(args, "include")
        _exclude_values = self.get_values_from_args(args, "exclude")
        if _include_values is not None:
            object.__setattr__(
                self,
                "include_values",
                _include_values,
            )
        if _exclude_values is not None:
            object.__setattr__(
                self,
                "exclude_values",
                _exclude_values,
            )

    @abstractmethod
    def is_manifest_object_in_scope(
        self, manifest_object: "ManifestObject", manifest: Optional["Manifest"] = None
    ) -> bool:
        """Whether the object is in scope for the current check.

        Args:
            manifest_object: ManifestObject instance.
            manifest: Manifest instance

        Returns:
            True if the object is in scope, False otherwise.

        Raises:
            NotImplementedError: if the object does not support this filter method.
        """
        ...

    @property
    @abstractmethod
    def arg_name_suffix(self) -> str:
        """Suffix of this filter method's CLI argument names."""
        ...

    def get_values_from_args(
        self,
        args: Namespace | None,
        prefix: str,
    ) -> set[Any] | None:
        """Parse the included/excluded values from CLI args.

        Args:
            args: CLI args Namespace instance.
            prefix: prefix of the argument name.

        Returns:
            A set of included values or None.
        """
        values = getattr(args, f"{prefix}_{self.arg_name_suffix}", None)
        if args is None or values is None:
            return None
        elif isinstance(values, Collection):
            return set(values)
        raise TypeError(f"{values} is not a Collection")

    @property
    def includes_summary(self) -> str:
        """String summary of included values."""
        return (
            f"{self.arg_name_suffix.replace('_', ' ')}: {', '.join(sorted(self.include_values))}"
            if self.include_values
            else ""
        )

    @property
    def excludes_summary(self) -> str:
        """String summary of excluded values."""
        return (
            f"{self.arg_name_suffix.replace('_', ' ')}: {', '.join(sorted(self.exclude_values))}"
            if self.exclude_values
            else ""
        )


class MaterializationFilterMethod(ManifestFilterMethod):
    """Method for filtering by materialization.

    Attributes:
        include_values: set of materializations to include.
        exclude_values: set of materializations to exclude.
    """

    include_values: set[str] | None = None
    exclude_values: set[str] | None = None

    @property
    def arg_name_suffix(self) -> str:
        """Suffix of this filter method's CLI argument names."""
        return "materializations"

    def is_manifest_object_in_scope(
        self, manifest_object: "ManifestObject", manifest: Optional["Manifest"] = None
    ) -> bool:
        """Whether the object is in scope for the current check.

        Args:
            manifest_object: ManifestObject instance.
            manifest: Manifest instance

        Returns:
            True if the object is in scope, False otherwise.

        Raises:
            NotImplementedError: if the object does not support this filter method.
        """
        materialized = getattr(manifest_object, "materialized", None)
        if materialized is None:
            raise NotImplementedError(
                f"{manifest_object} cannot be filtered by materialization."
            )
        excluded = (
            self.exclude_values is not None and materialized in self.exclude_values
        )
        included = self.include_values is None or materialized in self.include_values
        return included and not excluded


class TagFilterMethod(ManifestFilterMethod):
    """Method for filtering by tag.

    Attributes:
        include_values: set of tags to include.
        exclude_values: set of tags to exclude.
    """

    include_values: set[str] | None = None
    exclude_values: set[str] | None = None

    @property
    def arg_name_suffix(self) -> str:
        """Suffix of this filter method's CLI argument names."""
        return "tags"

    def is_manifest_object_in_scope(
        self, manifest_object: "ManifestObject", manifest: Optional["Manifest"] = None
    ) -> bool:
        """Whether the object is in scope for the current check.

        Args:
            manifest_object: ManifestObject instance.
            manifest: Manifest instance.

        Returns:
            True if the object is in scope, False otherwise.

        Raises:
            NotImplementedError: if the object does not support this filter method.
        """
        tags = getattr(manifest_object, "tags", None)
        if tags is None:
            raise NotImplementedError(f"{manifest_object} cannot be filtered by tags.")
        excluded = self.exclude_values is not None and bool(
            tags.intersection(self.exclude_values)
        )
        included = self.include_values is None or bool(
            tags.intersection(self.include_values)
        )
        return included and not excluded


class NamePatternFilterMethod(ManifestFilterMethod):
    """Method for filtering by name regex pattern.

    Attributes:
        include_values: set of name patterns to include.
        exclude_values: set of name patterns to exclude.
    """

    include_values: set[str] | None = None
    exclude_values: set[str] | None = None

    @property
    def arg_name_suffix(self) -> str:
        """Suffix of this filter method's CLI argument names."""
        return "name_patterns"

    def is_manifest_object_in_scope(
        self, manifest_object: "ManifestObject", manifest: Optional["Manifest"] = None
    ) -> bool:
        """Whether the object is in scope for the current check.

        Args:
            manifest_object: ManifestObject instance.
            manifest: Manifest instance.

        Returns:
            True if the object is in scope, False otherwise.

        Raises:
            NotImplementedError: if the object does not support this filter method.
        """
        excluded = self.exclude_values is not None and any(
            manifest_object.name_matches_regex(pattern)
            for pattern in self.exclude_values
        )
        included = self.include_values is None or any(
            manifest_object.name_matches_regex(pattern)
            for pattern in self.include_values
        )
        return included and not excluded


class PackageFilterMethod(ManifestFilterMethod):
    """Method for filtering by package name.

    Attributes:
        include_values: set of package names to include.
        exclude_values: set of package names to exclude.
    """

    include_values: set[str] | None = None
    exclude_values: set[str] | None = None

    @property
    def arg_name_suffix(self) -> str:
        """Suffix of this filter method's CLI argument names."""
        return "packages"

    def is_manifest_object_in_scope(
        self, manifest_object: "ManifestObject", manifest: Optional["Manifest"] = None
    ) -> bool:
        """Whether the object is in scope for the current check.

        Args:
            manifest_object: ManifestObject instance.
            manifest: Manifest instance.

        Returns:
            True if the object is in scope, False otherwise.

        Raises:
            NotImplementedError: if the object does not support this filter method.
        """
        excluded = (
            self.exclude_values is not None
            and manifest_object.package_name in self.exclude_values
        )
        included = (
            self.include_values is None
            or manifest_object.package_name in self.include_values
        )
        return included and not excluded


class ResourceTypeFilterMethod(ManifestFilterMethod):
    """Method for filtering by resource type.

    Attributes:
        include_values: set of resource types to include.
        exclude_values: set of resource types to exclude.
    """

    include_values: set[str] | None = None
    exclude_values: set[str] | None = None

    @property
    def arg_name_suffix(self) -> str:
        """Suffix of this filter method's CLI argument names."""
        return "resource_types"

    def is_manifest_object_in_scope(
        self, manifest_object: "ManifestObject", manifest: Optional["Manifest"] = None
    ) -> bool:
        """Whether the object is in scope for the current check.

        Args:
            manifest_object: ManifestObject instance.
            manifest: Manifest instance.

        Returns:
            True if the object is in scope, False otherwise.

        Raises:
            NotImplementedError: if the object does not support this filter method.
        """
        excluded = (
            self.exclude_values is not None
            and manifest_object.resource_type in self.exclude_values
        )
        included = (
            self.include_values is None
            or manifest_object.resource_type in self.include_values
        )
        return included and not excluded


class DirectParentsFilterMethod(ManifestFilterMethod):
    """Method for filtering by direct parents.

    Attributes:
        include_values: set of direct parents to include.
        exclude_values: set of direct parents to exclude.
    """

    include_values: set[str] | None = None
    exclude_values: set[str] | None = None

    @property
    def arg_name_suffix(self) -> str:
        """Suffix of this filter method's CLI argument names."""
        return "direct_parents"

    def is_manifest_object_in_scope(
        self, manifest_object: "ManifestObject", manifest: Optional["Manifest"] = None
    ) -> bool:
        """Whether the object is in scope for the current check.

        Args:
            manifest_object: ManifestObject instance.
            manifest: Manifest instance.

        Returns:
            True if the object is in scope, False otherwise.

        Raises:
            NotImplementedError: if the object does not support this filter method.
            ValueError: if manifest is None.
        """
        if manifest is None:
            raise ValueError("manifest cannot be None")
        excluded = self.exclude_values is not None and bool(
            get_direct_parents(
                manifest_object.unique_id, manifest=manifest
            ).intersection(self.exclude_values)
        )
        included = self.include_values is None or (
            bool(
                get_direct_parents(
                    manifest_object.unique_id, manifest=manifest
                ).intersection(self.include_values)
            )
        )
        return included and not excluded


class IndirectParentsFilterMethod(ManifestFilterMethod):
    """Method for filtering by indirect parents.

    Attributes:
        include_values: set of indirect parents to include.
        exclude_values: set of indirect parents to exclude.
    """

    include_values: set[str] | None = None
    exclude_values: set[str] | None = None

    @property
    def arg_name_suffix(self) -> str:
        """Suffix of this filter method's CLI argument names."""
        return "indirect_parents"

    def is_manifest_object_in_scope(
        self, manifest_object: "ManifestObject", manifest: Optional["Manifest"] = None
    ) -> bool:
        """Whether the object is in scope for the current check.

        Args:
            manifest_object: ManifestObject instance.
            manifest: Manifest instance.

        Returns:
            True if the object is in scope, False otherwise.

        Raises:
            NotImplementedError: if the object does not support this filter method.
            ValueError: if manifest is None.
        """
        if manifest is None:
            raise ValueError("manifest cannot be None")
        excluded = self.exclude_values is not None and bool(
            get_all_parents(
                manifest_object.unique_id,
                manifest=manifest,
                include_indirect=True,
            ).intersection(self.exclude_values)
        )
        included = self.include_values is None or (
            bool(
                get_all_parents(
                    manifest_object.unique_id,
                    manifest=manifest,
                    include_indirect=True,
                ).intersection(self.include_values)
            )
        )
        return included and not excluded


class DirectChildrenFilterMethod(ManifestFilterMethod):
    """Method for filtering by direct children.

    Attributes:
        include_values: set of direct children to include.
        exclude_values: set of direct children to exclude.
    """

    include_values: set[str] | None = None
    exclude_values: set[str] | None = None

    @property
    def arg_name_suffix(self) -> str:
        """Suffix of this filter method's CLI argument names."""
        return "direct_children"

    def is_manifest_object_in_scope(
        self, manifest_object: "ManifestObject", manifest: Optional["Manifest"] = None
    ) -> bool:
        """Whether the object is in scope for the current check.

        Args:
            manifest_object: ManifestObject instance.
            manifest: Manifest instance.

        Returns:
            True if the object is in scope, False otherwise.

        Raises:
            NotImplementedError: if the object does not support this filter method.
            ValueError: if manifest is None.
        """
        if manifest is None:
            raise ValueError("manifest cannot be None")
        excluded = self.exclude_values is not None and bool(
            get_direct_children(
                manifest_object.unique_id, manifest=manifest
            ).intersection(self.exclude_values)
        )
        included = self.include_values is None or (
            bool(
                get_direct_children(
                    manifest_object.unique_id, manifest=manifest
                ).intersection(self.include_values)
            )
        )
        return included and not excluded


class IndirectChildrenFilterMethod(ManifestFilterMethod):
    """Method for filtering by indirect children.

    Attributes:
        include_values: set of indirect children to include.
        exclude_values: set of indirect children to exclude.
    """

    include_values: set[str] | None = None
    exclude_values: set[str] | None = None

    @property
    def arg_name_suffix(self) -> str:
        """Suffix of this filter method's CLI argument names."""
        return "indirect_children"

    def is_manifest_object_in_scope(
        self, manifest_object: "ManifestObject", manifest: Optional["Manifest"] = None
    ) -> bool:
        """Whether the object is in scope for the current check.

        Args:
            manifest_object: ManifestObject instance.
            manifest: Manifest instance.

        Returns:
            True if the object is in scope, False otherwise.

        Raises:
            NotImplementedError: if the object does not support this filter method.
            ValueError: if manifest is None.
        """
        if manifest is None:
            raise ValueError("manifest cannot be None")
        excluded = self.exclude_values is not None and bool(
            get_all_children(
                manifest_object.unique_id,
                manifest=manifest,
                include_indirect=True,
            ).intersection(self.exclude_values)
        )
        included = self.include_values is None or (
            bool(
                get_all_children(
                    manifest_object.unique_id,
                    manifest=manifest,
                    include_indirect=True,
                ).intersection(self.include_values)
            )
        )
        return included and not excluded


class PathFilterMethod(ManifestFilterMethod):
    """Method for filtering by resource path.

    Attributes:
        include_values: set of resource paths to include.
        exclude_values: set of resource paths to exclude.
    """

    include_values: set[Path] | None = None
    exclude_values: set[Path] | None = None

    @property
    def arg_name_suffix(self) -> str:
        """Suffix of this filter method's CLI argument names."""
        return "node_paths"

    def is_manifest_object_in_scope(
        self, manifest_object: "ManifestObject", manifest: Optional["Manifest"] = None
    ) -> bool:
        """Whether the object is in scope for the current check.

        Args:
            manifest_object: ManifestObject instance.
            manifest: Manifest instance.

        Returns:
            True if the object is in scope, False otherwise.

        Raises:
            NotImplementedError: if the object does not support this filter method.
        """
        excluded = self.exclude_values is not None and any(
            Path(manifest_object.data["original_file_path"]).is_relative_to(path)
            for path in self.exclude_values
        )
        included = self.include_values is None or any(
            Path(manifest_object.data["original_file_path"]).is_relative_to(path)
            for path in self.include_values
        )
        return included and not excluded

    @property
    def includes_summary(self) -> str:
        """String summary of included values."""
        return (
            f"paths: {', '.join(sorted(path.as_posix() for path in self.include_values))}"
            if self.include_values
            else ""
        )

    @property
    def excludes_summary(self) -> str:
        """String summary of excluded values."""
        return (
            f"paths: {', '.join(sorted(path.as_posix() for path in self.exclude_values))}"
            if self.exclude_values
            else ""
        )


@dataclass(eq=True, frozen=True)
class ManifestFilterConditions:
    """Conditions to filter manifest objects by.

    Attributes:
        filter_methods: tuple of ManifestObjectFilter instances
    """

    args: InitVar[Namespace | None] = None
    filter_methods: tuple[ManifestFilterMethod, ...] = field(init=False)

    def __post_init__(self, args: Namespace | None) -> None:
        """Initialize the instance.

        Args:
            args: CLI args Namespace instance.
        """
        object.__setattr__(
            self,
            "filter_methods",
            (
                MaterializationFilterMethod(args),
                PathFilterMethod(args),
                PackageFilterMethod(args),
                NamePatternFilterMethod(args),
                ResourceTypeFilterMethod(args),
                TagFilterMethod(args),
                DirectParentsFilterMethod(args),
                IndirectParentsFilterMethod(args),
                DirectChildrenFilterMethod(args),
                IndirectChildrenFilterMethod(args),
            ),
        )

    def is_manifest_object_in_scope(
        self, manifest_object: "ManifestObject", manifest: Optional["Manifest"]
    ) -> bool:
        """Whether the object is in scope after all filter methods.

        Args:
            manifest_object: ManifestObject instance.
            manifest: Manifest instance.
        """
        for filter_method in self.filter_methods:
            try:
                if not filter_method.is_manifest_object_in_scope(
                    manifest_object, manifest
                ):
                    return False
            except NotImplementedError:
                pass
        return True

    @property
    def summary(self) -> str:
        """Summarise all the filter conditions in a block of text."""
        includes = [
            filter_method.includes_summary.strip()
            for filter_method in self.filter_methods
            if filter_method.includes_summary
        ]
        excludes = [
            filter_method.excludes_summary.strip()
            for filter_method in self.filter_methods
            if filter_method.excludes_summary
        ]
        return colour_message(
            ""
            + ("\nIncluding:\n\t" + "\n\t".join(includes) if includes else "")
            + ("\nExcluding:\n\t" + "\n\t".join(excludes) if excludes else ""),
            emphasis=ConsoleEmphasis.ITALIC,
        )
