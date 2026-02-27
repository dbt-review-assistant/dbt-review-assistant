import sys
from typing import Iterable
from unittest.mock import patch, Mock

import pytest

from checks.model_checks.model_columns_have_types import ModelColumnsHaveTypes


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
                        "column_1": {"name": "column_1", "data_type": "INT64"},
                        "column_2": {"name": "column_2", "data_type": "STRING"},
                    },
                },
                {
                    "unique_id": "another_model",
                    "columns": {
                        "column_1": {"name": "column_1", "data_type": "INT64"},
                        "column_2": {"name": "column_2", "data_type": "STRING"},
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
                        "column_1": {"name": "column_1", "data_type": "INT64"},
                        "column_2": {"name": "column_2", "data_type": "STRING"},
                    },
                },
                {
                    "unique_id": "another_model",
                    "columns": {
                        "column_1": {"name": "column_1", "data_type": "INT64"},
                        "column_2": {"name": "column_2"},
                    },
                },
            ],
            {"another_model.column_2"},
        ),
    ],
)
def test_model_columns_have_types_perform_checks(
    models: Iterable[dict[str, str]],
    expected_failures: set[str],
    tmpdir,
):
    with (
        patch.object(sys, "argv", return_value=[]),
        patch.object(ModelColumnsHaveTypes, "__call__"),
        patch(
            "checks.model_checks.model_columns_have_types.get_models_from_manifest",
            return_value=models,
        ) as mock_get_models_from_manifest,
    ):
        instance = ModelColumnsHaveTypes()
        instance.perform_check()
        assert instance.check_name == "model-columns-have-types"
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


def test_model_columns_have_descriptions_failure_message():
    with (
        patch.object(ModelColumnsHaveTypes, "failures"),
        patch.object(ModelColumnsHaveTypes, "parse_args"),
        patch.object(ModelColumnsHaveTypes, "__call__"),
        patch(
            "checks.model_checks.model_columns_have_types.object_missing_attribute_message"
        ) as mock_object_missing_attribute_message,
    ):
        instance = ModelColumnsHaveTypes()
        mock_object_missing_attribute_message.return_value = Mock()
        result = instance.failure_message
        mock_object_missing_attribute_message.assert_called_with(
            missing_attributes=instance.failures,
            object_type="model column",
            attribute_type="data_type",
        )
        assert result is mock_object_missing_attribute_message.return_value
