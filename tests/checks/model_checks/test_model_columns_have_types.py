from argparse import Namespace
from typing import Iterable
from unittest.mock import Mock, PropertyMock, patch

import pytest

from checks.model_checks.model_columns_have_types import ModelColumnsHaveTypes
from utils.check_abc import STANDARD_MODEL_ARGUMENTS
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
        patch.object(ModelColumnsHaveTypes, "__call__"),
        patch.object(
            ModelColumnsHaveTypes, "manifest", new_callable=PropertyMock
        ) as mock_manifest,
    ):
        columns = [
            column
            for model_data in models
            for column in ManifestModel(model_data).columns
        ]
        mock_in_scope_columns = PropertyMock(return_value=columns)
        type(mock_manifest.return_value).in_scope_model_columns = mock_in_scope_columns
        instance = ModelColumnsHaveTypes(Namespace())
        instance.perform_check()
        assert instance.check_name == "model-columns-have-types"
        assert instance.additional_arguments == STANDARD_MODEL_ARGUMENTS
        assert instance.failures == expected_failures
        mock_in_scope_columns.assert_called_once()


def test_model_columns_have_descriptions_failure_message():
    with (
        patch.object(ModelColumnsHaveTypes, "failures"),
        patch.object(ModelColumnsHaveTypes, "__call__"),
        patch(
            "checks.model_checks.model_columns_have_types.object_missing_attribute_message"
        ) as mock_object_missing_attribute_message,
    ):
        instance = ModelColumnsHaveTypes(Namespace())
        mock_object_missing_attribute_message.return_value = Mock()
        result = instance.failure_message
        mock_object_missing_attribute_message.assert_called_with(
            missing_attributes=instance.failures,
            object_type="model column",
            attribute_type="data_type",
        )
        assert result is mock_object_missing_attribute_message.return_value
