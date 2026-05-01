from argparse import Namespace
from typing import Iterable
from unittest.mock import Mock, PropertyMock, patch

import pytest

from checks.model_checks.model_column_descriptions_are_consistent import (
    ModelColumnsDescriptionsAreConsistent,
)
from utils.check_abc import STANDARD_MODEL_ARGUMENTS
from utils.manifest_object.node.model.model import ManifestModel


@pytest.mark.parametrize(
    ids=[
        "Two models, two column instances, all match",
        "Two models, two column instances, one mismatch",
    ],
    argnames=["models", "expected_descriptions"],
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
            {},
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
                        "column_2": {
                            "name": "column_2",
                            "description": "Different description",
                        },
                    },
                },
            ],
            {
                "column_2": [
                    {
                        "unique_id": "another_model.column_2",
                        "description": "Different description",
                    },
                    {"unique_id": "test_model.column_2", "description": "Column 2"},
                ]
            },
        ),
    ],
)
def test_model_column_descriptions_are_consistent_perform_checks(
    models: Iterable[dict[str, str]],
    expected_descriptions: dict[str, list[dict[str, str]]],
    tmpdir,
):
    with (
        patch.object(ModelColumnsDescriptionsAreConsistent, "__call__"),
        patch.object(
            ModelColumnsDescriptionsAreConsistent, "manifest", new_callable=PropertyMock
        ) as mock_manifest,
    ):
        columns = [
            column
            for model_data in models
            for column in ManifestModel(model_data).columns
        ]
        mock_in_scope_columns = PropertyMock(return_value=columns)
        type(mock_manifest.return_value).in_scope_model_columns = mock_in_scope_columns
        instance = ModelColumnsDescriptionsAreConsistent(Namespace())
        instance.perform_check()
        assert instance.check_name == "model-column-descriptions-are-consistent"
        assert instance.additional_arguments == STANDARD_MODEL_ARGUMENTS
        assert instance.descriptions == expected_descriptions
        mock_in_scope_columns.assert_called_once()


@pytest.mark.parametrize(
    ids=[
        "No descriptions",
        "One description",
    ],
    argnames=("descriptions", "expected_result"),
    argvalues=[
        ({}, False),
        (
            {
                "column_2": [
                    {"model": "another_model", "description": "Different description"},
                    {"model": "test_model", "description": "Column 2"},
                ]
            },
            True,
        ),
    ],
)
def test_model_column_descriptions_are_consistent_has_failures(
    descriptions: dict[str, list[dict[str, str]]], expected_result: bool
):
    with (
        patch.object(
            ModelColumnsDescriptionsAreConsistent, "descriptions", descriptions
        ),
        patch.object(ModelColumnsDescriptionsAreConsistent, "__call__"),
    ):
        instance = ModelColumnsDescriptionsAreConsistent(Namespace())
        assert expected_result is instance.has_failures


def test_model_column_descriptions_are_consistent_failure_message():
    with (
        patch.object(ModelColumnsDescriptionsAreConsistent, "descriptions"),
        patch.object(ModelColumnsDescriptionsAreConsistent, "__call__"),
        patch(
            "checks.model_checks.model_column_descriptions_are_consistent.inconsistent_column_descriptions_message"
        ) as mock_inconsistent_column_descriptions_message,
    ):
        instance = ModelColumnsDescriptionsAreConsistent(Namespace())
        mock_inconsistent_column_descriptions_message.return_value = Mock()
        result = instance.failure_message
        mock_inconsistent_column_descriptions_message.assert_called_with(
            descriptions=instance.descriptions,
        )
        assert result is mock_inconsistent_column_descriptions_message.return_value
