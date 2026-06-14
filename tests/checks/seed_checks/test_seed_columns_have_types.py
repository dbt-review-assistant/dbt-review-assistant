from argparse import Namespace
from typing import Iterable
from unittest.mock import Mock, PropertyMock, patch

import pytest

from checks.seed_checks.seed_columns_have_types import SeedColumnsHaveTypes
from utils.check_abc import STANDARD_SEED_ARGUMENTS
from utils.manifest_object.node.node import ManifestSeed


@pytest.mark.parametrize(
    ids=[
        "two seeds, both pass",
        "two seeds, one fails",
    ],
    argnames=["seeds", "expected_failures"],
    argvalues=[
        (
            [
                {
                    "unique_id": "test_seed",
                    "columns": {
                        "col_1": {"name": "col_1", "data_type": "INT64"},
                        "col_2": {"name": "col_2", "data_type": "STRING"},
                    },
                },
                {
                    "unique_id": "another_seed",
                    "columns": {
                        "col_1": {"name": "col_1", "data_type": "INT64"},
                    },
                },
            ],
            set(),
        ),
        (
            [
                {
                    "unique_id": "test_seed",
                    "columns": {
                        "col_1": {"name": "col_1", "data_type": "INT64"},
                        "col_2": {"name": "col_2", "data_type": "STRING"},
                    },
                },
                {
                    "unique_id": "another_seed",
                    "columns": {
                        "col_1": {"name": "col_1", "data_type": "INT64"},
                        "col_2": {"name": "col_2"},
                    },
                },
            ],
            {"another_seed.col_2"},
        ),
    ],
)
def test_seed_columns_have_types_perform_checks(
    seeds: Iterable[dict],
    expected_failures: set[str],
):
    with (
        patch.object(SeedColumnsHaveTypes, "__call__"),
        patch.object(
            SeedColumnsHaveTypes, "manifest", new_callable=PropertyMock
        ) as mock_manifest,
    ):
        columns = [
            column for seed_data in seeds for column in ManifestSeed(seed_data).columns
        ]
        mock_in_scope_seed_columns = PropertyMock(return_value=columns)
        type(
            mock_manifest.return_value
        ).in_scope_seed_columns = mock_in_scope_seed_columns
        instance = SeedColumnsHaveTypes(Namespace())
        instance.perform_check()
        assert instance.check_name == "seed-columns-have-types"
        assert instance.additional_arguments == STANDARD_SEED_ARGUMENTS
        assert instance.failures == expected_failures
        mock_in_scope_seed_columns.assert_called_once()


def test_seed_columns_have_types_failure_message():
    with (
        patch.object(SeedColumnsHaveTypes, "failures"),
        patch.object(SeedColumnsHaveTypes, "__call__"),
        patch(
            "checks.seed_checks.seed_columns_have_types.object_missing_attribute_message"
        ) as mock_object_missing_attribute_message,
    ):
        instance = SeedColumnsHaveTypes(Namespace())
        mock_object_missing_attribute_message.return_value = Mock()
        result = instance.failure_message
        mock_object_missing_attribute_message.assert_called_with(
            missing_attributes=instance.failures,
            object_type="seed column",
            attribute_type="data_type",
        )
        assert result is mock_object_missing_attribute_message.return_value
