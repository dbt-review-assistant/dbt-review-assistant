import sys
from typing import Iterable
from unittest.mock import Mock, PropertyMock, patch

import pytest

from checks.model_checks.models_have_properties_file import ModelsHavePropertiesFile
from utils.manifest_filter_conditions import ManifestFilterConditions
from utils.manifest_object.node.model.model import ManifestModel


@pytest.mark.parametrize(
    ids=[
        "two models, both pass",
        "two models, one fails",
    ],
    argnames=["models", "expected_failures"],
    argvalues=[
        (
            [
                {"unique_id": "test_model", "patch_path": "path/to/properties.yml"},
                {"unique_id": "another_model", "patch_path": "path/to/properties.yml"},
            ],
            set(),
        ),
        (
            [
                {"unique_id": "test_model", "patch_path": "path/to/properties.yml"},
                {
                    "unique_id": "another_model",
                },
            ],
            {"another_model"},
        ),
    ],
)
def test_models_have_properties_file_perform_checks(
    models: Iterable[dict[str, str]],
    expected_failures: set[str],
    tmpdir,
):
    with (
        patch.object(sys, "argv", return_value=[]),
        patch.object(ModelsHavePropertiesFile, "__call__"),
        patch.object(
            ModelsHavePropertiesFile, "manifest", new_callable=PropertyMock
        ) as mock_manifest,
    ):
        mock_in_scope_models = PropertyMock(
            return_value=[
                ManifestModel(model_data, ManifestFilterConditions())
                for model_data in models
            ]
        )
        type(mock_manifest.return_value).in_scope_models = mock_in_scope_models
        instance = ModelsHavePropertiesFile()
        instance.perform_check()
        assert instance.check_name == "models-have-properties-file"
        assert instance.additional_arguments == [
            "include_materializations",
            "include_tags",
            "include_packages",
            "include_node_paths",
            "include_name_patterns",
            "exclude_materializations",
            "exclude_tags",
            "exclude_packages",
            "exclude_node_paths",
            "exclude_name_patterns",
        ]
        assert instance.failures == expected_failures
        mock_in_scope_models.assert_called()


def test_models_have_properties_file_failure_message():
    with (
        patch.object(ModelsHavePropertiesFile, "failures"),
        patch.object(ModelsHavePropertiesFile, "parse_args"),
        patch.object(ModelsHavePropertiesFile, "__call__"),
        patch(
            "checks.model_checks.models_have_properties_file.object_missing_attribute_message"
        ) as mock_object_missing_attribute_message,
    ):
        instance = ModelsHavePropertiesFile()
        mock_object_missing_attribute_message.return_value = Mock()
        result = instance.failure_message
        mock_object_missing_attribute_message.assert_called_with(
            missing_attributes=instance.failures,
            object_type="model",
            attribute_type="properties YAML file",
        )
        assert result is mock_object_missing_attribute_message.return_value
