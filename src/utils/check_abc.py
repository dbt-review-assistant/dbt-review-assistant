"""Abstract Base Classes for checks."""

import logging
from abc import ABC, abstractmethod
from argparse import Namespace
from typing import Collection

from utils.artifact_data import Catalog, Manifest
from utils.console_formatting import (
    ConsoleEmphasis,
    check_status_header,
    colour_message,
)
from utils.manifest_filter_conditions import ManifestFilterConditions


class Check(ABC):
    """Abstract base class for generic checks.

    Attributes:
        args: check arguments
    """

    check_name: str
    additional_arguments: list[str]

    def __init__(self, args: Namespace) -> None:
        """Initialise and call the instance."""
        self.args: Namespace = args
        self()

    @property
    def filter_conditions(self) -> ManifestFilterConditions:
        """Filter conditions for filtering objects from the manifest."""
        return ManifestFilterConditions(
            _include_materializations=getattr(
                self.args, "include_materializations", None
            ),
            _include_tags=getattr(self.args, "include_tags", None),
            _include_packages=getattr(self.args, "include_packages", None),
            _include_paths=getattr(self.args, "include_node_paths", None),
            _include_name_patterns=getattr(self.args, "include_name_patterns", None),
            _exclude_materializations=getattr(
                self.args, "exclude_materializations", None
            ),
            _exclude_tags=getattr(self.args, "exclude_tags", None),
            _exclude_packages=getattr(self.args, "exclude_packages", None),
            _exclude_paths=getattr(self.args, "exclude_node_paths", None),
            _exclude_name_patterns=getattr(self.args, "exclude_name_patterns", None),
        )

    @abstractmethod
    def perform_check(self) -> None:
        """Execute the check logic."""
        ...

    @property
    @abstractmethod
    def failure_message(self) -> str:
        """Compile a failure log message."""
        ...

    @property
    @abstractmethod
    def has_failures(self) -> bool:
        """Determine whether any entities failed the check."""
        ...

    def __call__(self) -> None:
        """Run the check end-to-end.

        Raises:
             SystemExit with the result of the check
        """
        logging.info(
            f"""{
                colour_message(
                    f"Performing check: {self.check_name}",
                    emphasis=ConsoleEmphasis.BOLD,
                )
            }\n\n{self.filter_conditions.summary}\n"""
        )
        self.perform_check()
        if self.has_failures:
            logging.error(
                f"{check_status_header(f'{self.check_name}: FAIL', False)}\n\n{self.failure_message}\n\n{80 * '_'}\n"
            )
        logging.info(
            f"{check_status_header(f'{self.check_name}: PASS', True)}\n\n{80 * '_'}\n"
        )

    @property
    def manifest(self) -> Manifest:
        """Manifest instance to check against."""
        return Manifest(
            manifest_dir=self.args.manifest_dir,
            filter_conditions=self.filter_conditions,
            filepaths=getattr(self.args, "files", None),
        )


class ManifestCheck(Check, ABC):
    """Abstract base class for manifest-based checks.

    Attributes:
        failures: Collection of check failure items
    """

    failures: Collection = ()

    @property
    def has_failures(self) -> bool:
        """Determine whether any entities failed the check."""
        return bool(self.failures)


class ManifestVsCatalogComparison(Check, ABC):
    """Abstract base class for manifest vs. catalog comparison checks.

    Attributes:
        manifest_items: Collection of manifest items for comparison
        catalog_items: Collection of catalog items for comparison
    """

    manifest_items: set[str] | dict[str, str | None]
    catalog_items: set[str] | dict[str, str]

    @property
    def has_failures(self) -> bool:
        """Determine whether any entities failed the check."""
        return bool(self.manifest_items != self.catalog_items)

    @property
    def catalog(self) -> Catalog:
        """Catalog instance to check against."""
        return Catalog(catalog_dir=self.args.catalog_dir)
