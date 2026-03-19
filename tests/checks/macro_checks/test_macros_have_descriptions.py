import sys
from typing import Iterable
from unittest.mock import Mock, PropertyMock, patch

import pytest

from checks.macro_checks.macros_have_descriptions import MacrosHaveDescriptions
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
                    "description": "test_description",
                },
                {
                    "unique_id": "another_macro",
                    "description": "test_description",
                },
            ],
            set(),
        ),
        (
            [
                {
                    "unique_id": "test_macro",
                    "description": "test_description",
                },
                {
                    "unique_id": "another_macro",
                    "description": "",
                },
            ],
            {"another_macro"},
        ),
    ],
)
def test_macros_have_descriptions_perform_checks(
    macros: Iterable[dict[str, str]],
    expected_failures: set[str],
    tmpdir,
):
    with (
        patch.object(sys, "argv", return_value=[]),
        patch.object(MacrosHaveDescriptions, "__call__"),
        patch.object(
            MacrosHaveDescriptions, "manifest", new_callable=PropertyMock
        ) as mock_manifest,
    ):
        mock_in_scope_macros = PropertyMock(
            return_value=[
                Macro(macro_data, ManifestFilterConditions()) for macro_data in macros
            ]
        )
        type(mock_manifest.return_value).in_scope_macros = mock_in_scope_macros
        instance = MacrosHaveDescriptions()
        instance.perform_check()
        assert instance.check_name == "macros-have-descriptions"
        assert instance.additional_arguments == [
            "include_packages",
            "include_tags",
            "exclude_packages",
            "exclude_tags",
        ]
        assert instance.failures == expected_failures
        mock_in_scope_macros.assert_called_once()


def test_macros_have_descriptions_failure_message():
    with (
        patch.object(MacrosHaveDescriptions, "failures"),
        patch.object(MacrosHaveDescriptions, "parse_args"),
        patch.object(MacrosHaveDescriptions, "__call__"),
        patch(
            "checks.macro_checks.macros_have_descriptions.object_missing_attribute_message"
        ) as mock_object_missing_attribute_message,
    ):
        instance = MacrosHaveDescriptions()
        mock_object_missing_attribute_message.return_value = Mock()
        result = instance.failure_message
        mock_object_missing_attribute_message.assert_called_with(
            missing_attributes=instance.failures,
            object_type="macro",
            attribute_type="description",
        )
        assert result is mock_object_missing_attribute_message.return_value
