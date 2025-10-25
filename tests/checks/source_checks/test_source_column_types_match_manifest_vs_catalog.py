import sys
from typing import Iterable
from unittest.mock import Mock, patch

import pytest

from checks.source_checks.source_column_types_match_manifest_vs_catalog import (
    SourceColumnTypesMatchManifestVsCatalog,
)


@pytest.mark.parametrize(
    ids=[
        "One source, types match",
        "Two sources, types mismatch",
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
                        "column_1": {"name": "column_1", "data_type": "INT64"},
                        "column_2": {"name": "column_2", "data_type": "STRING"},
                    },
                },
            ],
            [
                {
                    "unique_id": "test_source",
                    "columns": {
                        "column_1": {"type": "INT64"},
                        "column_2": {"type": "STRING"},
                    },
                },
            ],
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
            [
                {
                    "unique_id": "test_source",
                    "columns": {
                        "column_1": {"type": "FLOAT64"},
                        "column_2": {"type": "JSON"},
                    },
                },
                {
                    "unique_id": "another_source",
                    "columns": {
                        "column_3": {"type": "FLOAT64"},
                        "column_4": {"type": "JSON"},
                    },
                },
            ],
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
            [
                {
                    "unique_id": "test_source",
                    "columns": {
                        "column_1": {"type": "INT64"},
                        "column_2": {"type": "STRING"},
                    },
                },
            ],
            {},
            {},
        ),
    ],
)
def test_source_column_types_match_manifest_vs_catalog_perform_checks(
    manifest_sources: Iterable[dict[str, str]],
    catalog_nodes: list[dict[str, str]],
    expected_manifest_items: set[str],
    expected_catalog_items: set[str],
    tmpdir,
):
    with (
        patch.object(sys, "argv", return_value=[]),
        patch.object(SourceColumnTypesMatchManifestVsCatalog, "__call__"),
        patch(
            "checks.source_checks.source_column_types_match_manifest_vs_catalog.get_sources_from_manifest",
            return_value=manifest_sources,
        ) as mock_get_sources_from_manifest,
        patch(
            "checks.source_checks.source_column_types_match_manifest_vs_catalog.get_json_artifact_data",
            return_value={
                "sources": {node["unique_id"]: node for node in catalog_nodes}
            },
        ) as mock_get_json_artifact_data,
    ):
        instance = SourceColumnTypesMatchManifestVsCatalog()
        instance.perform_check()
        assert instance.check_name == "source-column-types-match-manifest-vs-catalog"
        assert instance.additional_arguments == [
            "include_tags",
            "include_packages",
            "include_node_paths",
            "exclude_tags",
            "exclude_packages",
            "exclude_node_paths",
        ]
        assert instance.catalog_items == expected_catalog_items
        assert instance.manifest_items == expected_manifest_items
        mock_get_json_artifact_data.assert_called_once_with(
            instance.args.manifest_dir / "catalog.json",
        )
        mock_get_sources_from_manifest.assert_called_once_with(
            manifest_dir=instance.args.manifest_dir,
            filter_conditions=instance.filter_conditions,
        )


def test_source_column_types_match_manifest_vs_catalog_failure_message():
    with (
        patch.object(SourceColumnTypesMatchManifestVsCatalog, "manifest_items"),
        patch.object(SourceColumnTypesMatchManifestVsCatalog, "catalog_items"),
        patch.object(SourceColumnTypesMatchManifestVsCatalog, "parse_args"),
        patch.object(SourceColumnTypesMatchManifestVsCatalog, "__call__"),
        patch(
            "checks.source_checks.source_column_types_match_manifest_vs_catalog.manifest_vs_catalog_column_type_mismatch_message"
        ) as mock_manifest_vs_catalog_column_type_mismatch_message,
    ):
        instance = SourceColumnTypesMatchManifestVsCatalog()
        mock_manifest_vs_catalog_column_type_mismatch_message.return_value = Mock()
        result = instance.failure_message
        mock_manifest_vs_catalog_column_type_mismatch_message.assert_called_with(
            catalog_columns=instance.catalog_items,
            manifest_columns=instance.manifest_items,
        )
        assert (
            result is mock_manifest_vs_catalog_column_type_mismatch_message.return_value
        )
