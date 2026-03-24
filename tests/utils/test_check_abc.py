import logging
from argparse import Namespace
from pathlib import Path
from unittest.mock import Mock, call, patch

import pytest

from utils.check_abc import Check, ManifestCheck, ManifestVsCatalogComparison
from utils.console_formatting import (
    ConsoleEmphasis,
    check_status_header,
    colour_message,
)
from utils.manifest_filter_conditions import ManifestFilterConditions

ADDITIONAL_ARGUMENTS = [
    "include_materializations",
    "include_packages",
    "include_tags",
    "exclude_materializations",
    "exclude_packages",
    "exclude_tags",
]


class ConcreteCheck(Check):
    manifest_args: None | set = None
    sql_args: None | set = None
    check_name: str = "test-concrete-check"
    additional_arguments = ADDITIONAL_ARGUMENTS
    failures: bool = False

    def perform_check(self) -> None:
        """Execute the check logic."""
        pass

    @property
    def has_failures(self) -> bool:
        """Determine whether any entities failed the check."""
        return bool(self.failures)

    @property
    def failure_message(self) -> str:
        """Compile a failure log message."""
        return ""


def test_check_init():
    with (
        patch.object(Check, "__call__") as mock_call,
    ):
        args = Mock()
        instance = ConcreteCheck(args)
        mock_call.assert_called_once()
        assert instance.args is args


def test_check_check_name():
    mock_args = Mock()
    with (
        patch.object(Check, "__call__"),
    ):
        instance = ConcreteCheck(mock_args)
        assert instance.check_name == "test-concrete-check"


def test_check_additional_arguments():
    mock_args = Mock()
    with (
        patch.object(Check, "__call__"),
    ):
        instance = ConcreteCheck(mock_args)
        assert instance.additional_arguments == ADDITIONAL_ARGUMENTS


def test_check_filter_conditions():
    mock_args = Namespace(
        include_materializations=["table"],
        include_packages=["test_dbt_package"],
        include_tags=["test_tag"],
        include_node_paths=[Path("test/path/")],
        exclude_materializations=["view"],
        exclude_packages=["another_dbt_package"],
        exclude_tags=["another_tag"],
        exclude_node_paths=[Path("another/path/")],
    )
    with (
        patch.object(Check, "__call__"),
    ):
        instance = ConcreteCheck(mock_args)
        assert instance.filter_conditions == ManifestFilterConditions(
            _include_resource_types=None,
            _include_materializations=["table"],
            _include_packages=["test_dbt_package"],
            _include_tags=["test_tag"],
            _include_paths=[Path("test/path/")],
            _exclude_resource_types=None,
            _exclude_materializations=["view"],
            _exclude_packages=["another_dbt_package"],
            _exclude_tags=["another_tag"],
            _exclude_paths=[Path("another/path/")],
        )


@pytest.mark.parametrize(
    ids=["with failures", "no failures"],
    argnames=["has_failures"],
    argvalues=[
        (True,),
        (False,),
    ],
)
def test_check_call(has_failures: bool):
    mock_args = Namespace(
        include_materializations=["table"],
        include_packages=["test_dbt_package"],
        include_tags=["test_tag"],
        exclude_materializations=["view"],
        exclude_packages=["another_dbt_package"],
        exclude_tags=["another_tag"],
    )
    with (
        patch.object(ConcreteCheck, "perform_check") as mock_perform_check,
        patch.object(logging, "info") as mock_info,
        patch.object(logging, "error") as mock_error,
        patch.object(ConcreteCheck, "__init__", return_value=None),
    ):
        instance = ConcreteCheck(mock_args)
        instance.args = mock_args
        instance.failures = has_failures
        instance()
        mock_perform_check.assert_called_once()
        mock_info.assert_has_calls(
            [
                call(
                    f"""{
                        colour_message(
                            f"Performing check: {instance.check_name}",
                            emphasis=ConsoleEmphasis.BOLD,
                        )
                    }\n\n{instance.filter_conditions.summary}\n"""
                ),
                call(
                    f"{check_status_header(f'{instance.check_name}: PASS', True)}\n\n{80 * '_'}\n"
                ),
            ]
        )
        if has_failures:
            mock_error.assert_called_with(
                f"{check_status_header(f'{instance.check_name}: FAIL', False)}\n\n{instance.failure_message}\n\n{80 * '_'}\n"
            )


class ConcreteManifestCheck(ManifestCheck):
    manifest_args: None | set = None
    sql_args: None | set = None
    check_name: str = "test-concrete-check"
    additional_arguments = ADDITIONAL_ARGUMENTS
    failures: set = set()

    def perform_check(self) -> None:
        """Execute the check logic."""
        pass

    @property
    def failure_message(self) -> str:
        """Compile a failure log message."""
        return ""


@pytest.mark.parametrize(
    ids=["empty", "with failures"],
    argnames=["failures", "expected_return"],
    argvalues=[
        (
            [],
            False,
        ),
        (
            ["something-failed"],
            True,
        ),
    ],
)
def test_manifest_check_has_failures(failures, expected_return):
    mock_args = Namespace(
        include_materializations=["table"],
        include_packages=["test_dbt_package"],
        include_tags=["test_tag"],
        exclude_materializations=["view"],
        exclude_packages=["another_dbt_package"],
        exclude_tags=["another_tag"],
    )
    with (
        patch.object(Check, "__call__"),
        patch.object(Check, "__init__", return_value=None),
    ):
        instance = ConcreteManifestCheck(mock_args)
        instance.args = mock_args
        instance.failures = failures
        assert instance.has_failures is expected_return


def test_check_manifest():
    mock_args = Namespace(
        include_materializations=["table"],
        include_packages=["test_dbt_package"],
        include_tags=["test_tag"],
        exclude_materializations=["view"],
        exclude_packages=["another_dbt_package"],
        exclude_tags=["another_tag"],
        manifest_dir=Path("test/path/"),
        files=[Path("test/model.sql"), Path("test/schema.yml")],
    )
    mock_manifest_instance = Mock()
    with (
        patch.object(Check, "__call__"),
        patch(
            "utils.check_abc.Manifest", return_value=mock_manifest_instance
        ) as mock_manifest,
    ):
        instance = ConcreteCheck(mock_args)
        assert instance.manifest is mock_manifest_instance
        mock_manifest.assert_called_with(
            manifest_dir=mock_args.manifest_dir,
            filter_conditions=instance.filter_conditions,
            filepaths=mock_args.files,
        )


class ConcreteManifestVsCatalogComparison(ManifestVsCatalogComparison):
    manifest_args: None | set = None
    sql_args: None | set = None
    check_name: str = "test-concrete-check"
    additional_arguments = ADDITIONAL_ARGUMENTS
    failures: bool = False

    def perform_check(self) -> None:
        """Execute the check logic."""
        pass

    @property
    def failure_message(self) -> str:
        """Compile a failure log message."""
        return ""


def test_manifest_vs_catalog_comparison_check_manifest():
    mock_args = Namespace(
        include_materializations=["table"],
        include_packages=["test_dbt_package"],
        include_tags=["test_tag"],
        exclude_materializations=["view"],
        exclude_packages=["another_dbt_package"],
        exclude_tags=["another_tag"],
        manifest_dir=Path("test/path/"),
        files=[Path("test/model.sql"), Path("test/schema.yml")],
    )
    mock_manifest_instance = Mock()
    with (
        patch.object(Check, "__call__"),
        patch(
            "utils.check_abc.Manifest", return_value=mock_manifest_instance
        ) as mock_manifest,
    ):
        instance = ConcreteManifestVsCatalogComparison(mock_args)
        assert instance.manifest is mock_manifest_instance
        mock_manifest.assert_called_with(
            manifest_dir=mock_args.manifest_dir,
            filter_conditions=instance.filter_conditions,
            filepaths=mock_args.files,
        )


def test_manifest_vs_catalog_comparison_check_catalog():
    mock_args = Namespace(
        include_materializations=["table"],
        include_packages=["test_dbt_package"],
        include_tags=["test_tag"],
        exclude_materializations=["view"],
        exclude_packages=["another_dbt_package"],
        exclude_tags=["another_tag"],
        catalog_dir=Path("test/path/"),
        files=[Path("test/model.sql"), Path("test/schema.yml")],
    )
    mock_catalog_instance = Mock()
    with (
        patch.object(Check, "__call__"),
        patch(
            "utils.check_abc.Catalog", return_value=mock_catalog_instance
        ) as mock_catalog,
    ):
        instance = ConcreteManifestVsCatalogComparison(mock_args)
        assert instance.catalog is mock_catalog_instance
        mock_catalog.assert_called_with(
            catalog_dir=instance.args.catalog_dir,
        )


@pytest.mark.parametrize(
    ids=["has failures", "no failures"],
    argnames=["manifest_items", "catalog_items", "expected_return"],
    argvalues=[
        (
            {"test"},
            {"test"},
            False,
        ),
        (
            {"test"},
            {"test_test"},
            True,
        ),
    ],
)
def test_manifest_vs_catalog_comparison_has_failures(
    manifest_items, catalog_items, expected_return
):
    mock_args = Namespace(
        include_materializations=["table"],
        include_packages=["test_dbt_package"],
        include_tags=["test_tag"],
        exclude_materializations=["view"],
        exclude_packages=["another_dbt_package"],
        exclude_tags=["another_tag"],
        files=[Path("test/model.sql"), Path("test/schema.yml")],
    )
    with (
        patch.object(Check, "__call__"),
    ):
        instance = ConcreteManifestVsCatalogComparison(mock_args)
        instance.manifest_items = manifest_items
        instance.catalog_items = catalog_items
        assert instance.has_failures is expected_return
