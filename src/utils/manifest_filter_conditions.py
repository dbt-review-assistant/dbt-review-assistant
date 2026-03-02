from pathlib import Path
from typing import Collection, Any

from utils.console_formatting import colour_message, ConsoleEmphasis


class ManifestFilterConditions:
    """Conditions to filter manifest objects by.

    Attributes:
        include_materializations: materialization types to be included. Only applicable to models.
        exclude_materializations: materialization types to be excluded. Only applicable to models.
        include_packages: dbt packages to be included.
        exclude_packages: dbt packages to be excluded.
        include_tags: tags to be included.
        exclude_tags: tags to be excluded.
        include_paths: node paths to be included.
        exclude_paths: node paths to be excluded.
    """

    def __init__(
        self,
        include_materializations: Collection[str] | None = None,
        include_tags: Collection[str] | None = None,
        include_packages: Collection[str] | None = None,
        include_paths: Collection[Path] | None = None,
        include_resource_types: Collection[Path] | None = None,
        exclude_materializations: Collection[str] | None = None,
        exclude_tags: Collection[str] | None = None,
        exclude_packages: Collection[str] | None = None,
        exclude_paths: Collection[Path] | None = None,
        exclude_resource_types: Collection[Path] | None = None,
    ) -> None:
        """Initialize the instance.

        Args:
            include_materializations: materialization types to be included. Only applicable to models.
            exclude_materializations: materialization types to be excluded. Only applicable to models.
            include_packages: dbt packages to be included.
            exclude_packages: dbt packages to be excluded.
            include_tags: tags to be included.
            exclude_tags: tags to be excluded.
            include_paths: paths to be included.
            exclude_paths: paths to be excluded.
            include_resource_types: resource types to be included.
            exclude_resource_types: resource types to be excluded.
        """
        self.include_materializations = (
            set(include_materializations) if include_materializations else None
        )
        self.include_tags = set(include_tags) if include_tags else None
        self.include_packages = set(include_packages) if include_packages else None
        self.include_paths = set(include_paths) if include_paths else None
        self.include_resource_types = (
            set(include_resource_types) if include_resource_types else None
        )
        self.exclude_materializations = (
            set(exclude_materializations) if exclude_materializations else None
        )
        self.exclude_tags = set(exclude_tags) if exclude_tags else None
        self.exclude_packages = set(exclude_packages) if exclude_packages else None
        self.exclude_paths = set(exclude_paths) if exclude_paths else None
        self.exclude_resource_types = (
            set(exclude_resource_types) if exclude_resource_types else None
        )

    @property
    def summary(self) -> str:
        """Summarise all the filter conditions in a block of text."""
        includes: list[str] = []
        excludes: list[str] = []
        if self.include_resource_types:
            includes.append(
                f"resource types: {', '.join(sorted(path.as_posix() for path in self.include_resource_types))}"
            )
        if self.exclude_resource_types:
            excludes.append(
                f"resource types: {', '.join(sorted(path.as_posix() for path in self.exclude_resource_types))}"
            )
        if self.include_materializations:
            includes.append(
                f"materialized: {', '.join(sorted(self.include_materializations))}"
            )
        if self.include_tags:
            includes.append(f"tags: {', '.join(sorted(self.include_tags))}")
        if self.include_packages:
            includes.append(f"packages: {', '.join(sorted(self.include_packages))}")
        if self.include_paths:
            includes.append(
                f"paths: {', '.join(sorted(path.as_posix() for path in self.include_paths))}"
            )
        if self.exclude_materializations:
            excludes.append(
                f"materialized: {', '.join(sorted(self.exclude_materializations))}"
            )
        if self.exclude_tags:
            excludes.append(f"tags: {', '.join(sorted(self.exclude_tags))}")
        if self.exclude_packages:
            excludes.append(f"packages: {', '.join(sorted(self.exclude_packages))}")
        if self.exclude_paths:
            excludes.append(
                f"paths: {', '.join(sorted(path.as_posix() for path in self.exclude_paths))}"
            )
        return colour_message(
            ""
            + ("Including:\n\t" + "\n\t".join(includes) if includes else "")
            + ("\nExcluding:\n\t" + "\n\t".join(excludes) if excludes else ""),
            emphasis=ConsoleEmphasis.ITALIC,
        )

    def __eq__(self, other: Any) -> bool:
        """Test for equality of ManifestFilterConditions instances."""
        if not isinstance(other, ManifestFilterConditions):
            return False
        return all(
            getattr(self, attr) == getattr(other, attr)
            for attr in [
                "include_resource_types",
                "include_materializations",
                "include_tags",
                "include_packages",
                "include_node_paths",
                "exclude_resource_types",
                "exclude_materializations",
                "exclude_tags",
                "exclude_packages",
                "exclude_node_paths",
            ]
        )
