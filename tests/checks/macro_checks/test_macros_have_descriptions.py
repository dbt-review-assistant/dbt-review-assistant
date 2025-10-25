import sys
from typing import Iterable
from unittest.mock import patch, Mock

import pytest

from checks.macro_checks.macros_have_descriptions import MacrosHaveDescriptions


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
        patch(
            "checks.macro_checks.macros_have_descriptions.get_macros_from_manifest",
            return_value=macros,
        ) as mock_get_macros_from_manifest,
    ):
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
        mock_get_macros_from_manifest.assert_called_once_with(
            manifest_dir=instance.args.manifest_dir,
            filter_conditions=instance.filter_conditions,
        )


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
