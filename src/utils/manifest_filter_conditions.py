from dataclasses import dataclass, Field, field, InitVar
from pathlib import Path
from typing import Collection, Any

from utils.console_formatting import colour_message, ConsoleEmphasis


def set_default(value):
    return set(value) if value else None

@dataclass(eq=True, frozen=True)
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
    include_materializations: set[str] | None = field(init=False, default=None)
    include_tags: set[str] | None = field(init=False, default=None)
    include_packages: set[str] | None = field(init=False, default=None)
    include_paths: set[Path] | None = field(init=False, default=None)
    include_resource_types: set[str] | None = field(init=False, default=None)
    exclude_materializations: set[str] | None = field(init=False, default=None)
    exclude_tags: set[str] | None = field(init=False, default=None)
    exclude_packages: set[str] | None = field(init=False, default=None)
    exclude_paths: set[Path] | None = field(init=False, default=None)
    exclude_resource_types: set[str] | None = field(init=False, default=None)
    _include_materializations: InitVar[Collection[str] | None] = None  # NOSONAR
    _include_tags: InitVar[Collection[str] | None] = None  # NOSONAR
    _include_packages: InitVar[Collection[str] | None] = None  # NOSONAR
    _include_paths: InitVar[Collection[Path] | None] = None  # NOSONAR
    _include_resource_types: InitVar[Collection[str] | None] = None  # NOSONAR
    _exclude_materializations: InitVar[Collection[str] | None] = None  # NOSONAR
    _exclude_tags: InitVar[Collection[str] | None] = None  # NOSONAR
    _exclude_packages: InitVar[Collection[str] | None] = None  # NOSONAR
    _exclude_paths: InitVar[Collection[Path] | None] = None  # NOSONAR
    _exclude_resource_types: InitVar[Collection[str] | None] = None  # NOSONAR

    def __post_init__(
            self,
            _include_materializations: Collection[str] | None,
            _include_tags: Collection[str] | None,
            _include_packages: Collection[str] | None,
            _include_paths: Collection[Path] | None,
            _include_resource_types: Collection[str] | None,
            _exclude_materializations: Collection[str] | None,
            _exclude_tags: Collection[str] | None,
            _exclude_packages: Collection[str] | None,
            _exclude_paths: Collection[Path] | None,
            _exclude_resource_types: Collection[str] | None,
        ) -> None:
        """Initialize the instance."""
        if _include_materializations:
            object.__setattr__(
                self,
                "include_materializations",
                set(_include_materializations),
            )
        if _include_tags:
            object.__setattr__(
                self,
                "include_tags",
                set(_include_tags),
            )
        if _include_packages:
            object.__setattr__(
                self,
                "include_packages",
                set(_include_packages),
            )
        if _include_paths:
            object.__setattr__(
                self,
                "include_paths",
                set(_include_paths),
            )
        if _include_resource_types:
            object.__setattr__(
                self,
                "include_resource_types",
                set(_include_resource_types),
            )
        if _exclude_materializations:
            object.__setattr__(
                self,
                "exclude_materializations",
                set(_exclude_materializations),
            )
        if _exclude_tags:
            object.__setattr__(
                self,
                "exclude_tags",
                set(_exclude_tags),
            )
        if _exclude_packages:
            object.__setattr__(
                self,
                "exclude_packages",
                set(_exclude_packages),
            )
        if _exclude_paths:
            object.__setattr__(
                self,
                "exclude_paths",
                set(_exclude_paths),
            )
        if _exclude_resource_types:
            object.__setattr__(
                self,
                "exclude_resource_types",
                set(_exclude_resource_types),
            )

    @property
    def summary(self) -> str:
        """Summarise all the filter conditions in a block of text."""
        includes: list[str] = []
        excludes: list[str] = []
        if self.include_resource_types:
            includes.append(
                f"resource types: {', '.join(sorted(self.include_resource_types))}"
            )
        if self.exclude_resource_types:
            excludes.append(
                f"resource types: {', '.join(sorted(self.exclude_resource_types))}"
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
