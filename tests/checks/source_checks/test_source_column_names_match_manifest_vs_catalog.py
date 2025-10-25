import sys
from typing import Iterable
from unittest.mock import Mock, patch

import pytest

from checks.source_checks.source_column_names_match_manifest_vs_catalog import (
    SourceColumnNamesMatchManifestVsCatalog,
)


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
            [
                {
                    "unique_id": "test_source",
                    "columns": {
                        "column_1": {},
                        "column_2": {},
                    },
                },
            ],
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
            [
                {
                    "unique_id": "test_source",
                    "columns": {
                        "column_1": {},
                        "column_2": {},
                    },
                },
                {
                    "unique_id": "another_source",
                    "columns": {
                        "column_3": {},
                        "column_4": {},
                    },
                },
            ],
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
            [
                {
                    "unique_id": "test_source",
                    "columns": {
                        "column_1": {},
                        "column_2": {},
                    },
                },
            ],
            set(),
            set(),
        ),
    ],
)
def test_source_column_names_match_manifest_vs_catalog_perform_checks(
    manifest_sources: Iterable[dict[str, str]],
    catalog_nodes: list[dict[str, str]],
    expected_manifest_items: set[str],
    expected_catalog_items: set[str],
    tmpdir,
):
    with (
        patch.object(sys, "argv", return_value=[]),
        patch.object(SourceColumnNamesMatchManifestVsCatalog, "__call__"),
        patch(
            "checks.source_checks.source_column_names_match_manifest_vs_catalog.get_sources_from_manifest",
            return_value=manifest_sources,
        ) as mock_get_sources_from_manifest,
        patch(
            "checks.source_checks.source_column_names_match_manifest_vs_catalog.get_json_artifact_data",
            return_value={
                "sources": {node["unique_id"]: node for node in catalog_nodes}
            },
        ) as mock_get_json_artifact_data,
    ):
        instance = SourceColumnNamesMatchManifestVsCatalog()
        instance.perform_check()
        assert instance.check_name == "source-column-names-match-manifest-vs-catalog"
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


def test_source_column_names_match_manifest_vs_catalog_failure_message():
    with (
        patch.object(SourceColumnNamesMatchManifestVsCatalog, "manifest_items"),
        patch.object(SourceColumnNamesMatchManifestVsCatalog, "catalog_items"),
        patch.object(SourceColumnNamesMatchManifestVsCatalog, "parse_args"),
        patch.object(SourceColumnNamesMatchManifestVsCatalog, "__call__"),
        patch(
            "checks.source_checks.source_column_names_match_manifest_vs_catalog.manifest_vs_catalog_column_name_mismatch_message"
        ) as mock_manifest_vs_catalog_column_name_mismatch_message,
    ):
        instance = SourceColumnNamesMatchManifestVsCatalog()
        mock_manifest_vs_catalog_column_name_mismatch_message.return_value = Mock()
        result = instance.failure_message
        mock_manifest_vs_catalog_column_name_mismatch_message.assert_called_with(
            catalog_columns=instance.catalog_items,
            manifest_columns=instance.manifest_items,
        )
        assert (
            result is mock_manifest_vs_catalog_column_name_mismatch_message.return_value
        )
