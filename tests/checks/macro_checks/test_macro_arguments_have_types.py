import sys
from argparse import Namespace
from typing import Iterable
from unittest.mock import Mock, PropertyMock, patch

import pytest

from checks.macro_checks.macro_arguments_have_types import (
    MacroArgumentsHaveTypes,
)
from utils.manifest_filter_conditions import ManifestFilterConditions
from utils.manifest_object.macro import Macro


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
                        {"name": "argument_1", "type": "integer"},
                        {"name": "argument_2", "type": "string"},
                    ],
                },
                {
                    "unique_id": "another_macro",
                    "arguments": [
                        {"name": "argument_1", "type": "integer"},
                        {"name": "argument_2", "type": "string"},
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
                        {"name": "argument_1", "type": "integer"},
                        {"name": "argument_2", "type": "string"},
                    ],
                },
                {
                    "unique_id": "another_macro",
                    "arguments": [
                        {"name": "argument_1", "type": "integer"},
                        {"name": "argument_2", "type": ""},
                    ],
                },
            ],
            {"another_macro.argument_2"},
        ),
    ],
)
def test_macro_arguments_have_types_perform_checks(
    macros: Iterable[dict[str, str]],
    expected_failures: set[str],
    tmpdir,
):
    with (
        patch.object(MacroArgumentsHaveTypes, "__call__"),
        patch.object(
            MacroArgumentsHaveTypes, "manifest", new_callable=PropertyMock
        ) as mock_manifest,
    ):
        mock_in_scope_macros = PropertyMock(
            return_value=[
                Macro(macro_data, ManifestFilterConditions()) for macro_data in macros
            ]
        )
        type(mock_manifest.return_value).in_scope_macros = mock_in_scope_macros
        instance = MacroArgumentsHaveTypes(Namespace())
        instance.perform_check()
        assert instance.check_name == "macro-arguments-have-types"
        assert instance.additional_arguments == [
            "include_packages",
            "include_tags",
            "include_name_patterns",
            "exclude_packages",
            "exclude_tags",
            "exclude_name_patterns",
        ]
        assert instance.failures == expected_failures
        mock_in_scope_macros.assert_called()


def test_macro_arguments_have_descriptions_failure_message():
    with (
        patch.object(MacroArgumentsHaveTypes, "failures"),
        patch.object(MacroArgumentsHaveTypes, "__call__"),
        patch(
            "checks.macro_checks.macro_arguments_have_types.object_missing_attribute_message"
        ) as mock_object_missing_attribute_message,
    ):
        instance = MacroArgumentsHaveTypes(Namespace())
        mock_object_missing_attribute_message.return_value = Mock()
        result = instance.failure_message
        mock_object_missing_attribute_message.assert_called_with(
            missing_attributes=instance.failures,
            object_type="macro argument",
            attribute_type="type",
        )
        assert result is mock_object_missing_attribute_message.return_value
