from argparse import Namespace
from typing import Iterable
from unittest.mock import Mock, PropertyMock, patch

import pytest

from checks.model_checks.model_column_types_match_manifest_vs_catalog import (
    ModelColumnTypesMatchManifestVsCatalog,
)
from utils.catalog_object.catalog_table import CatalogTable
from utils.manifest_filter_conditions import ManifestFilterConditions
from utils.manifest_object.node.model.model import ManifestModel


@pytest.mark.parametrize(
    ids=[
        "One model, types match",
        "Two models, columns mismatch",
        "One disabled model",
    ],
    argnames=[
        "manifest_models",
        "catalog_nodes",
        "expected_manifest_items",
        "expected_catalog_items",
    ],
    argvalues=[
        (
            [
                {
                    "unique_id": "test_model",
                    "config": {"enabled": True},
                    "columns": {
                        "column_1": {"data_type": "INT64"},
                        "column_2": {"data_type": "STRING"},
                    },
                },
            ],
            {
                "test_model": {
                    "unique_id": "test_model",
                    "columns": {
                        "column_1": {"type": "INT64"},
                        "column_2": {"type": "STRING"},
                    },
                },
            },
            {"test_model.column_1": "INT64", "test_model.column_2": "STRING"},
            {"test_model.column_1": "INT64", "test_model.column_2": "STRING"},
        ),
        (
            [
                {
                    "unique_id": "test_model",
                    "config": {"enabled": True},
                    "columns": {
                        "column_1": {"data_type": "INT64"},
                        "column_2": {"data_type": "STRING"},
                    },
                },
                {
                    "unique_id": "another_model",
                    "config": {"enabled": True},
                    "columns": {
                        "column_3": {"data_type": "INT64"},
                        "column_4": {"data_type": "STRING"},
                    },
                },
            ],
            {
                "test_model": {
                    "unique_id": "test_model",
                    "config": {"enabled": True},
                    "columns": {
                        "column_1": {"type": "FLOAT64"},
                        "column_2": {"type": "JSON"},
                    },
                },
                "another_model": {
                    "unique_id": "another_model",
                    "config": {"enabled": True},
                    "columns": {
                        "column_3": {"type": "FLOAT64"},
                        "column_4": {"type": "JSON"},
                    },
                },
            },
            {
                "test_model.column_1": "INT64",
                "test_model.column_2": "STRING",
                "another_model.column_3": "INT64",
                "another_model.column_4": "STRING",
            },
            {
                "test_model.column_1": "FLOAT64",
                "test_model.column_2": "JSON",
                "another_model.column_3": "FLOAT64",
                "another_model.column_4": "JSON",
            },
        ),
        (
            [
                {
                    "unique_id": "test_model",
                    "config": {"enabled": False},
                    "columns": {
                        "column_1": {"data_type": "INT64"},
                        "column_2": {"data_type": "STRING"},
                    },
                },
            ],
            {
                "test_model": {
                    "unique_id": "test_model",
                    "columns": {
                        "column_1": {"type": "INT64"},
                        "column_2": {"type": "STRING"},
                    },
                },
            },
            {},
            {},
        ),
    ],
)
def test_model_column_types_match_manifest_vs_catalog_perform_checks(
    manifest_models: Iterable[dict[str, str]],
    catalog_nodes: dict[str, dict[str, str]],
    expected_manifest_items: set[str],
    expected_catalog_items: set[str],
    tmpdir,
):
    with (
        patch.object(ModelColumnTypesMatchManifestVsCatalog, "__call__"),
        patch.object(
            ModelColumnTypesMatchManifestVsCatalog,
            "manifest",
            new_callable=PropertyMock,
        ) as mock_manifest,
        patch.object(
            ModelColumnTypesMatchManifestVsCatalog, "catalog", new_callable=PropertyMock
        ) as mock_catalog,
    ):
        mock_in_scope_models = PropertyMock(
            return_value=[
                ManifestModel(model_data, ManifestFilterConditions())
                for model_data in manifest_models
            ]
        )
        type(mock_manifest.return_value).in_scope_models = mock_in_scope_models
        mock_catalog_nodes = PropertyMock(
            return_value={
                model_id: CatalogTable(model_data)
                for model_id, model_data in catalog_nodes.items()
            }
        )
        type(mock_catalog.return_value).nodes = mock_catalog_nodes
        instance = ModelColumnTypesMatchManifestVsCatalog(Namespace())
        instance.perform_check()
        assert instance.check_name == "model-column-types-match-manifest-vs-catalog"
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
        assert instance.catalog_items == expected_catalog_items
        assert instance.manifest_items == expected_manifest_items
        mock_catalog_nodes.assert_called_once()
        mock_in_scope_models.assert_called_once()


def test_model_column_types_match_manifest_vs_catalog_failure_message():
    with (
        patch.object(ModelColumnTypesMatchManifestVsCatalog, "manifest_items"),
        patch.object(ModelColumnTypesMatchManifestVsCatalog, "catalog_items"),
        patch.object(ModelColumnTypesMatchManifestVsCatalog, "__call__"),
        patch(
            "checks.model_checks.model_column_types_match_manifest_vs_catalog.manifest_vs_catalog_column_type_mismatch_message"
        ) as mock_manifest_vs_catalog_column_type_mismatch_message,
    ):
        instance = ModelColumnTypesMatchManifestVsCatalog(Namespace())
        mock_manifest_vs_catalog_column_type_mismatch_message.return_value = Mock()
        result = instance.failure_message
        mock_manifest_vs_catalog_column_type_mismatch_message.assert_called_with(
            catalog_columns=instance.catalog_items,
            manifest_columns=instance.manifest_items,
        )
        assert (
            result is mock_manifest_vs_catalog_column_type_mismatch_message.return_value
        )
