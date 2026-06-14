from argparse import Namespace
from typing import Iterable
from unittest.mock import Mock, PropertyMock, patch

import pytest

from checks.seed_checks.seed_column_names_match_manifest_vs_catalog import (
    SeedColumnNamesMatchManifestVsCatalog,
)
from utils.catalog_object.catalog_table import CatalogTable
from utils.check_abc import STANDARD_SEED_ARGUMENTS
from utils.manifest_object.node.node import ManifestSeed


@pytest.mark.parametrize(
    ids=[
        "one seed, columns match",
        "two seeds, columns mismatch",
        "one disabled seed",
    ],
    argnames=[
        "manifest_seeds",
        "catalog_nodes",
        "expected_manifest_items",
        "expected_catalog_items",
    ],
    argvalues=[
        (
            [
                {
                    "unique_id": "test_seed",
                    "config": {"enabled": True},
                    "columns": {
                        "column_1": {"name": "column_1"},
                        "column_2": {"name": "column_2"},
                    },
                },
            ],
            {
                "test_seed": {
                    "unique_id": "test_seed",
                    "columns": {
                        "column_1": {"name": "column_1"},
                        "column_2": {"name": "column_2"},
                    },
                },
            },
            {"test_seed.column_1", "test_seed.column_2"},
            {"test_seed.column_1", "test_seed.column_2"},
        ),
        (
            [
                {
                    "unique_id": "test_seed",
                    "config": {"enabled": True},
                    "columns": {"column_1": {"name": "column_1"}},
                },
                {
                    "unique_id": "another_seed",
                    "config": {"enabled": True},
                    "columns": {"column_2": {"name": "column_2"}},
                },
            ],
            {
                "test_seed": {
                    "unique_id": "test_seed",
                    "columns": {"column_3": {"name": "column_3"}},
                },
                "another_seed": {
                    "unique_id": "another_seed",
                    "columns": {"column_4": {"name": "column_4"}},
                },
            },
            {"test_seed.column_1", "another_seed.column_2"},
            {"test_seed.column_3", "another_seed.column_4"},
        ),
        (
            [
                {
                    "unique_id": "test_seed",
                    "config": {"enabled": False},
                    "columns": {"column_1": {"name": "column_1"}},
                },
            ],
            {
                "test_seed": {
                    "unique_id": "test_seed",
                    "columns": {"column_1": {"name": "column_1"}},
                },
            },
            set(),
            set(),
        ),
    ],
)
def test_seed_column_names_match_manifest_vs_catalog_perform_checks(
    manifest_seeds: Iterable[dict],
    catalog_nodes: dict,
    expected_manifest_items: set[str],
    expected_catalog_items: set[str],
):
    with (
        patch.object(SeedColumnNamesMatchManifestVsCatalog, "__call__"),
        patch.object(
            SeedColumnNamesMatchManifestVsCatalog, "manifest", new_callable=PropertyMock
        ) as mock_manifest,
        patch.object(
            SeedColumnNamesMatchManifestVsCatalog, "catalog", new_callable=PropertyMock
        ) as mock_catalog,
    ):
        columns = [
            column
            for seed_data in manifest_seeds
            for column in ManifestSeed(seed_data).columns
        ]
        mock_in_scope_seed_columns = PropertyMock(return_value=columns)
        type(
            mock_manifest.return_value
        ).in_scope_seed_columns = mock_in_scope_seed_columns
        mock_catalog_nodes = PropertyMock(
            return_value={
                seed_id: CatalogTable(seed_data)
                for seed_id, seed_data in catalog_nodes.items()
            }
        )
        type(mock_catalog.return_value).nodes = mock_catalog_nodes
        instance = SeedColumnNamesMatchManifestVsCatalog(Namespace())
        instance.perform_check()
        assert instance.check_name == "seed-column-names-match-manifest-vs-catalog"
        assert instance.additional_arguments == STANDARD_SEED_ARGUMENTS
        assert instance.catalog_items == expected_catalog_items
        assert instance.manifest_items == expected_manifest_items
        mock_catalog_nodes.assert_called_once()
        mock_in_scope_seed_columns.assert_called_once()


def test_seed_column_names_match_manifest_vs_catalog_failure_message():
    with (
        patch.object(SeedColumnNamesMatchManifestVsCatalog, "manifest_items"),
        patch.object(SeedColumnNamesMatchManifestVsCatalog, "catalog_items"),
        patch.object(SeedColumnNamesMatchManifestVsCatalog, "__call__"),
        patch(
            "checks.seed_checks.seed_column_names_match_manifest_vs_catalog.manifest_vs_catalog_column_name_mismatch_message"
        ) as mock_message,
    ):
        instance = SeedColumnNamesMatchManifestVsCatalog(Namespace())
        mock_message.return_value = Mock()
        result = instance.failure_message
        mock_message.assert_called_with(
            catalog_columns=instance.catalog_items,
            manifest_columns=instance.manifest_items,
        )
        assert result is mock_message.return_value
