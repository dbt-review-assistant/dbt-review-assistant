import sys
from typing import Iterable
from unittest.mock import patch, Mock, PropertyMock

import pytest

from checks.macro_checks.macro_arguments_have_descriptions import (
    MacroArgumentsHaveDescriptions,
)
from utils.manifest_filter_conditions import ManifestFilterConditions
from utils.manifest_object.macro import Macro
from utils.manifest_object.source.source import ManifestSource


@pytest.mark.parametrize(
    ids=[
        "two macros, both pass",
        "two macros, one fails",
    ],
    argnames=["macros", "expected_failures"],
    argvalues=[
        (
            [
                {
                    "unique_id": "test_macro",
                    "arguments": [
                        {"name": "argument_1", "description": "Argument 1"},
                        {"name": "argument_2", "description": "Argument 2"},
                    ],
                },
                {
                    "unique_id": "another_macro",
                    "arguments": [
                        {"name": "argument_1", "description": "Argument 1"},
                        {"name": "argument_2", "description": "Argument 2"},
                    ],
                },
            ],
            set(),
        ),
        (
            [
                {
                    "unique_id": "test_macro",
                    "arguments": [
                        {"name": "argument_1", "description": "Argument 1"},
                        {"name": "argument_2", "description": "Argument 2"},
                    ],
                },
                {
                    "unique_id": "another_macro",
                    "arguments": [
                        {"name": "argument_1", "description": "Argument 1"},
                        {"name": "argument_2", "description": ""},
                    ],
                },
            ],
            {"another_macro.argument_2"},
        ),
    ],
)
def test_macro_arguments_have_descriptions_perform_checks(
    macros: Iterable[dict[str, str]],
    expected_failures: set[str],
    tmpdir,
):
    with (
        patch.object(sys, "argv", return_value=[]),
        patch.object(MacroArgumentsHaveDescriptions, "__call__"),
        patch.object(
            MacroArgumentsHaveDescriptions, "manifest", new_callable=PropertyMock
        ) as mock_manifest,
    ):
        mock_in_scope_macros = PropertyMock(
            return_value=[
                Macro(macro_data, ManifestFilterConditions()) for macro_data in macros
            ]
        )
        type(mock_manifest.return_value).in_scope_macros = mock_in_scope_macros
        instance = MacroArgumentsHaveDescriptions()
        instance.perform_check()
        assert instance.check_name == "macro-arguments-have-descriptions"
        assert instance.additional_arguments == [
            "include_packages",
            "include_tags",
            "exclude_packages",
            "exclude_tags",
        ]
        assert instance.failures == expected_failures
        mock_in_scope_macros.assert_called()


def test_macro_arguments_have_descriptions_failure_message():
    with (
        patch.object(MacroArgumentsHaveDescriptions, "failures"),
        patch.object(MacroArgumentsHaveDescriptions, "parse_args"),
        patch.object(MacroArgumentsHaveDescriptions, "__call__"),
        patch(
            "checks.macro_checks.macro_arguments_have_descriptions.object_missing_attribute_message"
        ) as mock_object_missing_attribute_message,
    ):
        instance = MacroArgumentsHaveDescriptions()
        mock_object_missing_attribute_message.return_value = Mock()
        result = instance.failure_message
        mock_object_missing_attribute_message.assert_called_with(
            missing_attributes=instance.failures,
            object_type="macro argument",
            attribute_type="description",
        )
        assert result is mock_object_missing_attribute_message.return_value
