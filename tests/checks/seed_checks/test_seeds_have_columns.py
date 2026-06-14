from argparse import Namespace
from typing import Iterable
from unittest.mock import Mock, PropertyMock, patch

import pytest

from checks.seed_checks.seeds_have_columns import SeedsHaveColumns
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
                {"unique_id": "test_seed", "columns": {"col_1": {}}},
                {"unique_id": "another_seed", "columns": {"col_1": {}}},
            ],
            set(),
        ),
        (
            [
                {"unique_id": "test_seed", "columns": {"col_1": {}}},
                {"unique_id": "another_seed"},
            ],
            {"another_seed"},
        ),
    ],
)
def test_seeds_have_columns_perform_checks(
    seeds: Iterable[dict],
    expected_failures: set[str],
):
    with (
        patch.object(SeedsHaveColumns, "__call__"),
        patch.object(
            SeedsHaveColumns, "manifest", new_callable=PropertyMock
        ) as mock_manifest,
    ):
        mock_in_scope_seeds = PropertyMock(
            return_value=[ManifestSeed(seed_data) for seed_data in seeds]
        )
        type(mock_manifest.return_value).in_scope_seeds = mock_in_scope_seeds
        instance = SeedsHaveColumns(Namespace())
        instance.perform_check()
        assert instance.check_name == "seeds-have-columns"
        assert instance.additional_arguments == STANDARD_SEED_ARGUMENTS
        assert instance.failures == expected_failures
        mock_in_scope_seeds.assert_called_once()


def test_seeds_have_columns_failure_message():
    with (
        patch.object(SeedsHaveColumns, "failures"),
        patch.object(SeedsHaveColumns, "__call__"),
        patch(
            "checks.seed_checks.seeds_have_columns.object_missing_attribute_message"
        ) as mock_object_missing_attribute_message,
    ):
        instance = SeedsHaveColumns(Namespace())
        mock_object_missing_attribute_message.return_value = Mock()
        result = instance.failure_message
        mock_object_missing_attribute_message.assert_called_with(
            missing_attributes=instance.failures,
            object_type="seed",
            attribute_type="column",
        )
        assert result is mock_object_missing_attribute_message.return_value
