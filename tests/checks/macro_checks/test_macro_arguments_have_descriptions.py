import sys
from typing import Iterable
from unittest.mock import patch, Mock

import pytest

from checks.macro_checks.macro_arguments_have_descriptions import (
    MacroArgumentsHaveDescriptions,
)


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
        patch(
            "checks.macro_checks.macro_arguments_have_descriptions.get_macros_from_manifest",
            return_value=macros,
        ) as mock_get_macros_from_manifest,
    ):
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
        mock_get_macros_from_manifest.assert_called_once_with(
            manifest_dir=instance.args.manifest_dir,
            filter_conditions=instance.filter_conditions,
        )


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
