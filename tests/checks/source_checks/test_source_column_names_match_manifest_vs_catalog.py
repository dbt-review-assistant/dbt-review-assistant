from argparse import Namespace
from typing import Iterable
from unittest.mock import Mock, PropertyMock, patch

import pytest

from checks.source_checks.source_column_names_match_manifest_vs_catalog import (
    SourceColumnNamesMatchManifestVsCatalog,
)
from utils.catalog_object.catalog_table import CatalogTable
from utils.manifest_filter_conditions import ManifestFilterConditions
from utils.manifest_object.manifest_object import ManifestSource


@pytest.mark.parametrize(
    ids=[
        "One source, names match",
        "Two sources, names mismatch",
        "One disabled source",
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
                        "column_1": {},
                        "column_2": {},
                    },
                },
            ],
            {
                "test_source": {
                    "unique_id": "test_source",
                    "columns": {
                        "column_1": {},
                        "column_2": {},
                    },
                },
            },
            {"test_source.column_1", "test_source.column_2"},
            {"test_source.column_1", "test_source.column_2"},
        ),
        (
            [
                {
                    "unique_id": "test_source",
                    "config": {"enabled": True},
                    "columns": {
                        "column_1": {},
                        "column_2": {},
                    },
                },
                {
                    "unique_id": "another_source",
                    "config": {"enabled": True},
                    "columns": {
                        "column_3": {},
                        "column_4": {},
                    },
                },
            ],
            {
                "test_source": {
                    "unique_id": "test_source",
                    "columns": {
                        "column_1": {},
                        "column_2": {},
                    },
                },
                "another_source": {
                    "unique_id": "another_source",
                    "columns": {
                        "column_3": {},
                        "column_4": {},
                    },
                },
            },
            {
                "test_source.column_1",
                "test_source.column_2",
                "another_source.column_3",
                "another_source.column_4",
            },
            {
                "test_source.column_1",
                "test_source.column_2",
                "another_source.column_3",
                "another_source.column_4",
            },
        ),
        (
            [
                {
                    "unique_id": "test_source",
                    "config": {"enabled": False},
                    "columns": {
                        "column_1": {},
                        "column_2": {},
                    },
                },
            ],
            {
                "test_source": {
                    "unique_id": "test_source",
                    "columns": {
                        "column_1": {},
                        "column_2": {},
                    },
                },
            },
            set(),
            set(),
        ),
    ],
)
def test_source_column_names_match_manifest_vs_catalog_perform_checks(
    manifest_sources: Iterable[dict[str, str]],
    catalog_nodes: dict[str, dict[str, str]],
    expected_manifest_items: set[str],
    expected_catalog_items: set[str],
    tmpdir,
):
    with (
        patch.object(SourceColumnNamesMatchManifestVsCatalog, "__call__"),
        patch.object(
            SourceColumnNamesMatchManifestVsCatalog,
            "manifest",
            new_callable=PropertyMock,
        ) as mock_manifest,
        patch.object(
            SourceColumnNamesMatchManifestVsCatalog,
            "catalog",
            new_callable=PropertyMock,
        ) as mock_catalog,
    ):
        mock_in_scope_sources = PropertyMock(
            return_value=[
                ManifestSource(source_data, ManifestFilterConditions())
                for source_data in manifest_sources
            ]
        )
        type(mock_manifest.return_value).in_scope_sources = mock_in_scope_sources
        mock_catalog_sources = PropertyMock(
            return_value={
                source_id: CatalogTable(source_data)
                for source_id, source_data in catalog_nodes.items()
            }
        )
        type(mock_catalog.return_value).sources = mock_catalog_sources
        instance = SourceColumnNamesMatchManifestVsCatalog(Namespace())
        instance.perform_check()
        assert instance.check_name == "source-column-names-match-manifest-vs-catalog"
        assert instance.additional_arguments == [
            "include_tags",
            "include_packages",
            "include_node_paths",
            "include_name_patterns",
            "exclude_tags",
            "exclude_packages",
            "exclude_node_paths",
            "exclude_name_patterns",
        ]
        assert instance.catalog_items == expected_catalog_items
        assert instance.manifest_items == expected_manifest_items
        mock_catalog_sources.assert_called_once()
        mock_in_scope_sources.assert_called_once()


def test_source_column_names_match_manifest_vs_catalog_failure_message():
    with (
        patch.object(SourceColumnNamesMatchManifestVsCatalog, "manifest_items"),
        patch.object(SourceColumnNamesMatchManifestVsCatalog, "catalog_items"),
        patch.object(SourceColumnNamesMatchManifestVsCatalog, "__call__"),
        patch(
            "checks.source_checks.source_column_names_match_manifest_vs_catalog.manifest_vs_catalog_column_name_mismatch_message"
        ) as mock_manifest_vs_catalog_column_name_mismatch_message,
    ):
        instance = SourceColumnNamesMatchManifestVsCatalog(Namespace())
        mock_manifest_vs_catalog_column_name_mismatch_message.return_value = Mock()
        result = instance.failure_message
        mock_manifest_vs_catalog_column_name_mismatch_message.assert_called_with(
            catalog_columns=instance.catalog_items,
            manifest_columns=instance.manifest_items,
        )
        assert (
            result is mock_manifest_vs_catalog_column_name_mismatch_message.return_value
        )
