from argparse import Namespace
from unittest.mock import patch, Mock

import pytest

from utils.artifact_data import ManifestFilterConditions
from utils.check_abc import Check, ManifestCheck, ManifestVsCatalogComparison


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

    def __init__(self, failures) -> None:
        """Add __init__ method for helping with test setup."""
        self.failures = failures
        super().__init__()

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
    mock_args = Mock()
    with (
        patch.object(Check, "parse_args") as mock_parse_args,
        patch.object(Check, "__call__") as mock_call,
    ):
        mock_parse_args.return_value = mock_args
        instance = ConcreteCheck(False)
        mock_parse_args.assert_called_once()
        mock_call.assert_called_once()
        assert instance.args is mock_args


def test_check_check_name():
    mock_args = Mock()
    with (
        patch.object(Check, "parse_args") as mock_parse_args,
        patch.object(Check, "__call__") as mock_call,
    ):
        mock_parse_args.return_value = mock_args
        instance = ConcreteCheck(False)
        assert instance.check_name == "test-concrete-check"


def test_check_additional_arguments():
    mock_args = Mock()
    with (
        patch.object(Check, "parse_args") as mock_parse_args,
        patch.object(Check, "__call__") as mock_call,
    ):
        mock_parse_args.return_value = mock_args
        instance = ConcreteCheck(False)
        assert instance.additional_arguments == ADDITIONAL_ARGUMENTS


def test_check_filter_conditions():
    mock_args = Namespace(
        include_materializations=["table"],
        include_packages=["test_dbt_package"],
        include_tags=["test_tag"],
        exclude_materializations=["view"],
        exclude_packages=["another_dbt_package"],
        exclude_tags=["another_tag"],
    )
    with (
        patch.object(Check, "parse_args") as mock_parse_args,
        patch.object(Check, "__call__"),
    ):
        mock_parse_args.return_value = mock_args
        instance = ConcreteCheck(False)
        assert instance.filter_conditions == ManifestFilterConditions(
            include_materializations=["table"],
            include_packages=["test_dbt_package"],
            include_tags=["test_tag"],
            exclude_materializations=["view"],
            exclude_packages=["another_dbt_package"],
            exclude_tags=["another_tag"],
        )


@pytest.mark.parametrize(
    ids=["with failures", "no failures"],
    argnames=["has_failures", "expected_return"],
    argvalues=[
        (
            True,
            pytest.raises(SystemExit, match="test-concrete-check: FAIL"),
        ),
        (
            False,
            pytest.raises(SystemExit, match="0"),
        ),
    ],
)
def test_check_call(has_failures, expected_return):
    mock_args = Namespace(
        include_materializations=["table"],
        include_packages=["test_dbt_package"],
        include_tags=["test_tag"],
        exclude_materializations=["view"],
        exclude_packages=["another_dbt_package"],
        exclude_tags=["another_tag"],
    )
    with (
        expected_return,
        patch.object(Check, "parse_args") as mock_parse_args,
        patch.object(Check, "perform_check") as mock_perform_check,
    ):
        mock_parse_args.return_value = mock_args
        ConcreteCheck(has_failures)
        mock_perform_check.assert_called_once()


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
        patch.object(Check, "parse_args") as mock_parse_args,
        patch.object(Check, "__call__"),
    ):
        mock_parse_args.return_value = mock_args
        instance = ConcreteCheck(failures)
        assert instance.has_failures is expected_return
