import sys
from typing import Iterable
from unittest.mock import Mock, PropertyMock, patch

import pytest

from checks.model_checks.model_columns_have_descriptions import (
    ModelColumnsHaveDescriptions,
)
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
                {
                    "unique_id": "test_model",
                    "columns": {
                        "column_1": {"name": "column_1", "description": "Column 1"},
                        "column_2": {"name": "column_2", "description": "Column 2"},
                    },
                },
                {
                    "unique_id": "another_model",
                    "columns": {
                        "column_1": {"name": "column_1", "description": "Column 1"},
                        "column_2": {"name": "column_2", "description": "Column 2"},
                    },
                },
            ],
            set(),
        ),
        (
            [
                {
                    "unique_id": "test_model",
                    "columns": {
                        "column_1": {"name": "column_1", "description": "Column 1"},
                        "column_2": {"name": "column_2", "description": "Column 2"},
                    },
                },
                {
                    "unique_id": "another_model",
                    "columns": {
                        "column_1": {"name": "column_1", "description": "Column 1"},
                        "column_2": {"name": "column_2", "description": ""},
                    },
                },
            ],
            {"another_model.column_2"},
        ),
    ],
)
def test_model_columns_have_descriptions_perform_checks(
    models: Iterable[dict[str, str]],
    expected_failures: set[str],
    tmpdir,
):
    with (
        patch.object(sys, "argv", return_value=[]),
        patch.object(ModelColumnsHaveDescriptions, "__call__"),
        patch.object(
            ModelColumnsHaveDescriptions, "manifest", new_callable=PropertyMock
        ) as mock_manifest,
    ):
        mock_in_scope_models = PropertyMock(
            return_value=[
                ManifestModel(model_data, ManifestFilterConditions())
                for model_data in models
            ]
        )
        type(mock_manifest.return_value).in_scope_models = mock_in_scope_models
        instance = ModelColumnsHaveDescriptions()
        instance.perform_check()
        assert instance.check_name == "model-columns-have-descriptions"
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
        mock_in_scope_models.assert_called_once()


def test_model_columns_have_descriptions_failure_message():
    with (
        patch.object(ModelColumnsHaveDescriptions, "failures"),
        patch.object(ModelColumnsHaveDescriptions, "parse_args"),
        patch.object(ModelColumnsHaveDescriptions, "__call__"),
        patch(
            "checks.model_checks.model_columns_have_descriptions.object_missing_attribute_message"
        ) as mock_object_missing_attribute_message,
    ):
        instance = ModelColumnsHaveDescriptions()
        mock_object_missing_attribute_message.return_value = Mock()
        result = instance.failure_message
        mock_object_missing_attribute_message.assert_called_with(
            missing_attributes=instance.failures,
            object_type="model column",
            attribute_type="description",
        )
        assert result is mock_object_missing_attribute_message.return_value
