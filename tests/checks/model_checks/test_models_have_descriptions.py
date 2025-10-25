import sys
from typing import Iterable
from unittest.mock import patch, Mock

import pytest

from checks.model_checks.models_have_descriptions import ModelsHaveDescriptions


@pytest.mark.parametrize(
    ids=[
        "two models, both pass",
        "two models, one fails",
    ],
    argnames=["models", "expected_failures"],
    argvalues=[
        (
            [
                {
                    "unique_id": "test_model",
                    "description": "test_description",
                },
                {
                    "unique_id": "another_model",
                    "description": "test_description",
                },
            ],
            set(),
        ),
        (
            [
                {
                    "unique_id": "test_model",
                    "description": "test_description",
                },
                {
                    "unique_id": "another_model",
                    "description": "",
                },
            ],
            {"another_model"},
        ),
    ],
)
def test_models_have_descriptions_perform_checks(
    models: Iterable[dict[str, str]],
    expected_failures: set[str],
    tmpdir,
):
    with (
        patch.object(sys, "argv", return_value=[]),
        patch.object(ModelsHaveDescriptions, "__call__"),
        patch(
            "checks.model_checks.models_have_descriptions.get_models_from_manifest",
            return_value=models,
        ) as mock_get_models_from_manifest,
    ):
        instance = ModelsHaveDescriptions()
        instance.perform_check()
        assert instance.check_name == "models-have-descriptions"
        assert instance.additional_arguments == [
            "include_materializations",
            "include_tags",
            "include_packages",
            "include_node_paths",
            "exclude_materializations",
            "exclude_tags",
            "exclude_packages",
            "exclude_node_paths",
        ]
        assert instance.failures == expected_failures
        mock_get_models_from_manifest.assert_called_once_with(
            manifest_dir=instance.args.manifest_dir,
            filter_conditions=instance.filter_conditions,
        )


def test_models_have_descriptions_failure_message():
    with (
        patch.object(ModelsHaveDescriptions, "failures"),
        patch.object(ModelsHaveDescriptions, "parse_args"),
        patch.object(ModelsHaveDescriptions, "__call__"),
        patch(
            "checks.model_checks.models_have_descriptions.object_missing_attribute_message"
        ) as mock_object_missing_attribute_message,
    ):
        instance = ModelsHaveDescriptions()
        mock_object_missing_attribute_message.return_value = Mock()
        result = instance.failure_message
        mock_object_missing_attribute_message.assert_called_with(
            missing_attributes=instance.failures,
            object_type="model",
            attribute_type="description",
        )
        assert result is mock_object_missing_attribute_message.return_value
