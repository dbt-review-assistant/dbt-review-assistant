import sys
from argparse import Namespace
from typing import Iterable
from unittest.mock import Mock, PropertyMock, patch

import pytest

from checks.macro_checks.macro_names_must_match_pattern import MacroNamesMatchPattern
from utils.manifest_filter_conditions import ManifestFilterConditions
from utils.manifest_object.macro import Macro


@pytest.mark.parametrize(
    ids=[
        "two macros, both pass",
        "two macros, one fails",
    ],
    argnames=["macros", "pattern", "expected_failures"],
    argvalues=[
        (
            [
                {
                    "name": "test_macro",
                    "unique_id": "test_package.test_macro",
                },
                {
                    "name": "another_macro",
                    "unique_id": "test_package.another_macro",
                },
            ],
            "[a-z]",
            set(),
        ),
        (
            [
                {
                    "name": "test_macro",
                    "unique_id": "test_package.test_macro",
                },
                {
                    "name": "another_macro",
                    "unique_id": "test_package.another_macro",
                },
            ],
            "test_macro",
            {"test_package.another_macro"},
        ),
    ],
)
def test_macro_names_match_pattern_perform_checks(
    macros: Iterable[dict[str, str]],
    pattern: str,
    expected_failures: set[str],
    tmpdir,
):
    with (
        patch.object(MacroNamesMatchPattern, "__call__"),
        patch.object(
            MacroNamesMatchPattern, "manifest", new_callable=PropertyMock
        ) as mock_manifest,
    ):
        mock_in_scope_macros = PropertyMock(
            return_value=[
                Macro(macro_data, ManifestFilterConditions()) for macro_data in macros
            ]
        )
        type(mock_manifest.return_value).in_scope_macros = mock_in_scope_macros
        instance = MacroNamesMatchPattern(Namespace())
        instance.args.name_must_match_pattern = pattern
        instance.perform_check()
        assert instance.check_name == "macro-names-match-pattern"
        assert instance.additional_arguments == [
            "include_tags",
            "include_packages",
            "exclude_tags",
            "exclude_packages",
            "name_must_match_pattern",
        ]
        assert instance.failures == expected_failures
        mock_in_scope_macros.assert_called()


def test_macro_names_match_pattern_failure_message():
    with (
        patch.object(MacroNamesMatchPattern, "failures"),
        patch.object(MacroNamesMatchPattern, "__call__"),
        patch(
            "checks.macro_checks.macro_names_must_match_pattern.object_name_does_not_match_pattern"
        ) as mock_object_name_does_not_match_pattern,
    ):
        instance = MacroNamesMatchPattern(Namespace())
        pattern = "test_pattern"
        instance.args.name_must_match_pattern = pattern
        mock_object_name_does_not_match_pattern.return_value = Mock()
        result = instance.failure_message
        mock_object_name_does_not_match_pattern.assert_called_with(
            objects=instance.failures,
            object_type="macro",
            name_must_match_pattern=pattern,
        )
        assert result is mock_object_name_does_not_match_pattern.return_value
