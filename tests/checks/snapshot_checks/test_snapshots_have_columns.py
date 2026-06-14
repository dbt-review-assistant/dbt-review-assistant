from argparse import Namespace
from typing import Iterable
from unittest.mock import Mock, PropertyMock, patch

import pytest

from checks.snapshot_checks.snapshots_have_columns import SnapshotsHaveColumns
from utils.check_abc import STANDARD_SNAPSHOT_ARGUMENTS
from utils.manifest_object.node.node import ManifestSnapshot


@pytest.mark.parametrize(
    ids=[
        "two snapshots, both pass",
        "two snapshots, one fails",
    ],
    argnames=["snapshots", "expected_failures"],
    argvalues=[
        (
            [
                {"unique_id": "test_snapshot", "columns": {"col_1": {"name": "col_1"}}},
                {
                    "unique_id": "another_snapshot",
                    "columns": {"col_1": {"name": "col_1"}},
                },
            ],
            set(),
        ),
        (
            [
                {"unique_id": "test_snapshot", "columns": {"col_1": {"name": "col_1"}}},
                {"unique_id": "another_snapshot"},
            ],
            {"another_snapshot"},
        ),
    ],
)
def test_snapshots_have_columns_perform_checks(
    snapshots: Iterable[dict],
    expected_failures: set[str],
):
    with (
        patch.object(SnapshotsHaveColumns, "__call__"),
        patch.object(
            SnapshotsHaveColumns, "manifest", new_callable=PropertyMock
        ) as mock_manifest,
    ):
        mock_in_scope_snapshots = PropertyMock(
            return_value=[
                ManifestSnapshot(snapshot_data) for snapshot_data in snapshots
            ]
        )
        type(mock_manifest.return_value).in_scope_snapshots = mock_in_scope_snapshots
        instance = SnapshotsHaveColumns(Namespace())
        instance.perform_check()
        assert instance.check_name == "snapshots-have-columns"
        assert instance.additional_arguments == STANDARD_SNAPSHOT_ARGUMENTS
        assert instance.failures == expected_failures
        mock_in_scope_snapshots.assert_called_once()


def test_snapshots_have_columns_failure_message():
    with (
        patch.object(SnapshotsHaveColumns, "failures"),
        patch.object(SnapshotsHaveColumns, "__call__"),
        patch(
            "checks.snapshot_checks.snapshots_have_columns.object_missing_attribute_message"
        ) as mock_message,
    ):
        instance = SnapshotsHaveColumns(Namespace())
        mock_message.return_value = Mock()
        result = instance.failure_message
        mock_message.assert_called_with(
            missing_attributes=instance.failures,
            object_type="snapshot",
            attribute_type="column",
        )
        assert result is mock_message.return_value
