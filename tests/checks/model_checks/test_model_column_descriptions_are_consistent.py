import sys
from argparse import Namespace
from typing import Iterable
from unittest.mock import Mock, PropertyMock, patch

import pytest

from checks.model_checks.model_column_descriptions_are_consistent import (
    ModelColumnsDescriptionsAreConsistent,
)
from utils.manifest_filter_conditions import ManifestFilterConditions
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
                    {"model": "another_model", "description": "Different description"},
                    {"model": "test_model", "description": "Column 2"},
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
        mock_in_scope_models = PropertyMock(
            return_value=[
                ManifestModel(model_data, ManifestFilterConditions())
                for model_data in models
            ]
        )
        type(mock_manifest.return_value).in_scope_models = mock_in_scope_models
        instance = ModelColumnsDescriptionsAreConsistent(Namespace())
        instance.perform_check()
        assert instance.check_name == "model-column-descriptions-are-consistent"
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
        assert instance.descriptions == expected_descriptions
        mock_in_scope_models.assert_called_once()


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
