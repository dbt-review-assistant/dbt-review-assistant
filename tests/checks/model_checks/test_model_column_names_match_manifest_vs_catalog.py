import sys
from typing import Iterable
from unittest.mock import Mock, patch, PropertyMock

import pytest

from checks.model_checks.model_column_names_match_manifest_vs_catalog import (
    ModelColumnNamesMatchManifestVsCatalog,
)
from utils.catalog_object.catalog_table import CatalogTable
from utils.manifest_filter_conditions import ManifestFilterConditions
from utils.manifest_object.node.model.model import ManifestModel


@pytest.mark.parametrize(
    ids=[
        "One model, columns match",
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
                        "column_1": {"name": "column_1"},
                        "column_2": {"name": "column_2"},
                    },
                },
            ],
            {
                "test_model": {
                    "unique_id": "test_model",
                    "columns": {
                        "column_1": {"name": "column_1"},
                        "column_2": {"name": "column_2"},
                    },
                },
            },
            {"test_model.column_1", "test_model.column_2"},
            {"test_model.column_1", "test_model.column_2"},
        ),
        (
            [
                {
                    "unique_id": "test_model",
                    "config": {"enabled": True},
                    "columns": {
                        "column_1": {"name": "column_1"},
                        "column_2": {"name": "column_2"},
                    },
                },
                {
                    "unique_id": "another_model",
                    "config": {"enabled": True},
                    "columns": {
                        "column_3": {"name": "column_3"},
                        "column_4": {"name": "column_4"},
                    },
                },
            ],
            {
                "test_model": {
                    "unique_id": "test_model",
                    "columns": {
                        "column_5": {"name": "column_5"},
                        "column_6": {"name": "column_6"},
                    },
                },
                "another_model": {
                    "unique_id": "another_model",
                    "columns": {
                        "column_7": {"name": "column_7"},
                        "column_8": {"name": "column_8"},
                    },
                },
            },
            {
                "test_model.column_1",
                "test_model.column_2",
                "another_model.column_3",
                "another_model.column_4",
            },
            {
                "test_model.column_5",
                "test_model.column_6",
                "another_model.column_7",
                "another_model.column_8",
            },
        ),
        (
            [
                {
                    "unique_id": "test_model",
                    "config": {"enabled": False},
                    "columns": {
                        "column_1": {"name": "column_1"},
                    },
                },
            ],
            {
                "test_model": {
                    "unique_id": "test_model",
                    "columns": {
                        "column_1": {"name": "column_1"},
                    },
                },
            },
            set(),
            set(),
        ),
    ],
)
def test_model_column_names_match_manifest_vs_catalog_perform_checks(
    manifest_models: Iterable[dict[str, str]],
    catalog_nodes: dict[str, dict[str, str]],
    expected_manifest_items: set[str],
    expected_catalog_items: set[str],
    tmpdir,
):
    with (
        patch.object(sys, "argv", return_value=[]),
        patch.object(ModelColumnNamesMatchManifestVsCatalog, "__call__"),
        patch.object(
            ModelColumnNamesMatchManifestVsCatalog,
            "manifest",
            new_callable=PropertyMock,
        ) as mock_manifest,
        patch.object(
            ModelColumnNamesMatchManifestVsCatalog, "catalog", new_callable=PropertyMock
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
        instance = ModelColumnNamesMatchManifestVsCatalog()
        instance.perform_check()
        assert instance.check_name == "model-column-names-match-manifest-vs-catalog"
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
        assert instance.catalog_items == expected_catalog_items
        assert instance.manifest_items == expected_manifest_items
        mock_catalog_nodes.assert_called_once()
        mock_in_scope_models.assert_called_once()


def test_model_column_names_match_manifest_vs_catalog_failure_message():
    with (
        patch.object(ModelColumnNamesMatchManifestVsCatalog, "manifest_items"),
        patch.object(ModelColumnNamesMatchManifestVsCatalog, "catalog_items"),
        patch.object(ModelColumnNamesMatchManifestVsCatalog, "parse_args"),
        patch.object(ModelColumnNamesMatchManifestVsCatalog, "__call__"),
        patch(
            "checks.model_checks.model_column_names_match_manifest_vs_catalog.manifest_vs_catalog_column_name_mismatch_message"
        ) as mock_manifest_vs_catalog_column_name_mismatch_message,
    ):
        instance = ModelColumnNamesMatchManifestVsCatalog()
        mock_manifest_vs_catalog_column_name_mismatch_message.return_value = Mock()
        result = instance.failure_message
        mock_manifest_vs_catalog_column_name_mismatch_message.assert_called_with(
            catalog_columns=instance.catalog_items,
            manifest_columns=instance.manifest_items,
        )
        assert (
            result is mock_manifest_vs_catalog_column_name_mismatch_message.return_value
        )
