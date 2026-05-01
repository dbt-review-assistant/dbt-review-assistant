from argparse import Namespace
from typing import Iterable
from unittest.mock import Mock, PropertyMock, patch

import pytest

from checks.source_checks.source_column_types_match_manifest_vs_catalog import (
    SourceColumnTypesMatchManifestVsCatalog,
)
from utils.catalog_object.catalog_table import CatalogTable
from utils.check_abc import STANDARD_SOURCE_ARGUMENTS
from utils.manifest_object.manifest_object import ManifestSource


@pytest.mark.parametrize(
    ids=[
        "One source, types match",
        "Two sources, types mismatch",
        "One disabled source",
        "Extra column in catalog",
    ],
    argnames=[
        "manifest_sources",
        "catalog_nodes",
        "expected_manifest_items",
        "expected_catalog_items",
    ],
    argvalues=[
        (
            [
                {
                    "unique_id": "test_source",
                    "config": {"enabled": True},
                    "columns": {
                        "column_1": {"name": "column_1", "data_type": "INT64"},
                        "column_2": {"name": "column_2", "data_type": "STRING"},
                    },
                },
            ],
            {
                "test_source": {
                    "unique_id": "test_source",
                    "columns": {
                        "column_1": {"type": "INT64", "name": "column_1"},
                        "column_2": {"type": "STRING", "name": "column_2"},
                    },
                },
            },
            {"test_source.column_1": "INT64", "test_source.column_2": "STRING"},
            {"test_source.column_1": "INT64", "test_source.column_2": "STRING"},
        ),
        (
            [
                {
                    "unique_id": "test_source",
                    "config": {"enabled": True},
                    "columns": {
                        "column_1": {"name": "column_1", "data_type": "INT64"},
                        "column_2": {"name": "column_2", "data_type": "STRING"},
                    },
                },
                {
                    "unique_id": "another_source",
                    "config": {"enabled": True},
                    "columns": {
                        "column_3": {"name": "column_3", "data_type": "INT64"},
                        "column_4": {"name": "column_4", "data_type": "STRING"},
                    },
                },
            ],
            {
                "test_source": {
                    "unique_id": "test_source",
                    "columns": {
                        "column_1": {"type": "FLOAT64", "name": "column_1"},
                        "column_2": {"type": "JSON", "name": "column_2"},
                    },
                },
                "another_source": {
                    "unique_id": "another_source",
                    "columns": {
                        "column_3": {"type": "FLOAT64", "name": "column_3"},
                        "column_4": {"type": "JSON", "name": "column_4"},
                    },
                },
            },
            {
                "test_source.column_1": "INT64",
                "test_source.column_2": "STRING",
                "another_source.column_3": "INT64",
                "another_source.column_4": "STRING",
            },
            {
                "test_source.column_1": "FLOAT64",
                "test_source.column_2": "JSON",
                "another_source.column_3": "FLOAT64",
                "another_source.column_4": "JSON",
            },
        ),
        (
            [
                {
                    "unique_id": "test_source",
                    "config": {"enabled": False},
                    "columns": {
                        "column_1": {"name": "column_1", "data_type": "INT64"},
                        "column_2": {"name": "column_2", "data_type": "STRING"},
                    },
                },
            ],
            {
                "test_source": {
                    "unique_id": "test_source",
                    "columns": {
                        "column_1": {"type": "INT64", "name": "column_1"},
                        "column_2": {"type": "STRING", "name": "column_2"},
                    },
                },
            },
            {},
            {},
        ),
        (
            [
                {
                    "unique_id": "test_source",
                    "config": {"enabled": True},
                    "columns": {
                        "column_1": {"name": "column_1", "data_type": "INT64"},
                        "column_2": {"name": "column_2", "data_type": "STRING"},
                    },
                },
            ],
            {
                "test_source": {
                    "unique_id": "test_source",
                    "columns": {
                        "column_1": {"type": "INT64", "name": "column_1"},
                        "column_2": {"type": "STRING", "name": "column_2"},
                        "column_3": {"type": "STRING", "name": "column_3"},
                    },
                },
            },
            {"test_source.column_1": "INT64", "test_source.column_2": "STRING"},
            {
                "test_source.column_1": "INT64",
                "test_source.column_2": "STRING",
                "test_source.column_3": "STRING",
            },
        ),
    ],
)
def test_source_column_types_match_manifest_vs_catalog_perform_checks(
    manifest_sources: Iterable[dict[str, str]],
    catalog_nodes: dict[str, dict[str, str]],
    expected_manifest_items: set[str],
    expected_catalog_items: set[str],
    tmpdir,
):
    with (
        patch.object(SourceColumnTypesMatchManifestVsCatalog, "__call__"),
        patch.object(
            SourceColumnTypesMatchManifestVsCatalog,
            "manifest",
            new_callable=PropertyMock,
        ) as mock_manifest,
        patch.object(
            SourceColumnTypesMatchManifestVsCatalog,
            "catalog",
            new_callable=PropertyMock,
        ) as mock_catalog,
    ):
        columns = [
            column
            for source_data in manifest_sources
            for column in ManifestSource(source_data).columns
        ]
        mock_in_scope_source_columns = PropertyMock(return_value=columns)
        type(
            mock_manifest.return_value
        ).in_scope_source_columns = mock_in_scope_source_columns
        mock_catalog_sources = PropertyMock(
            return_value={
                source_id: CatalogTable(source_data)
                for source_id, source_data in catalog_nodes.items()
            }
        )
        type(mock_catalog.return_value).sources = mock_catalog_sources
        instance = SourceColumnTypesMatchManifestVsCatalog(Namespace())
        instance.perform_check()
        assert instance.check_name == "source-column-types-match-manifest-vs-catalog"
        assert instance.additional_arguments == STANDARD_SOURCE_ARGUMENTS
        assert instance.catalog_items == expected_catalog_items
        assert instance.manifest_items == expected_manifest_items
        mock_in_scope_source_columns.assert_called_once()
        mock_catalog_sources.assert_called_once()


def test_source_column_types_match_manifest_vs_catalog_failure_message():
    with (
        patch.object(SourceColumnTypesMatchManifestVsCatalog, "manifest_items"),
        patch.object(SourceColumnTypesMatchManifestVsCatalog, "catalog_items"),
        patch.object(SourceColumnTypesMatchManifestVsCatalog, "__call__"),
        patch(
            "checks.source_checks.source_column_types_match_manifest_vs_catalog.manifest_vs_catalog_column_type_mismatch_message"
        ) as mock_manifest_vs_catalog_column_type_mismatch_message,
    ):
        instance = SourceColumnTypesMatchManifestVsCatalog(Namespace())
        mock_manifest_vs_catalog_column_type_mismatch_message.return_value = Mock()
        result = instance.failure_message
        mock_manifest_vs_catalog_column_type_mismatch_message.assert_called_with(
            catalog_columns=instance.catalog_items,
            manifest_columns=instance.manifest_items,
        )
        assert (
            result is mock_manifest_vs_catalog_column_type_mismatch_message.return_value
        )
