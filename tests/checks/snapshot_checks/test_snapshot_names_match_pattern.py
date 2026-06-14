from argparse import Namespace
from typing import Iterable
from unittest.mock import Mock, PropertyMock, patch

import pytest

from checks.snapshot_checks.snapshot_names_match_pattern import (
    SnapshotNamesMatchPattern,
)
from utils.check_abc import STANDARD_SNAPSHOT_ARGUMENTS
from utils.manifest_object.node.node import ManifestSnapshot


@pytest.mark.parametrize(
    ids=[
        "two snapshots, both match",
        "two snapshots, one fails",
    ],
    argnames=["snapshots", "pattern", "expected_failures"],
    argvalues=[
        (
            [
                {"unique_id": "test_snapshot", "name": "stg_orders"},
                {"unique_id": "another_snapshot", "name": "stg_customers"},
            ],
            r"^stg_",
            set(),
        ),
        (
            [
                {"unique_id": "test_snapshot", "name": "stg_orders"},
                {"unique_id": "another_snapshot", "name": "orders"},
            ],
            r"^stg_",
            {"another_snapshot"},
        ),
    ],
)
def test_snapshot_names_match_pattern_perform_checks(
    snapshots: Iterable[dict],
    pattern: str,
    expected_failures: set[str],
):
    with (
        patch.object(SnapshotNamesMatchPattern, "__call__"),
        patch.object(
            SnapshotNamesMatchPattern, "manifest", new_callable=PropertyMock
        ) as mock_manifest,
    ):
        mock_in_scope_snapshots = PropertyMock(
            return_value=[ManifestSnapshot(s) for s in snapshots]
        )
        type(mock_manifest.return_value).in_scope_snapshots = mock_in_scope_snapshots
        instance = SnapshotNamesMatchPattern(Namespace(name_must_match_pattern=pattern))
        instance.perform_check()
        assert instance.check_name == "snapshot-names-match-pattern"
        assert instance.additional_arguments == STANDARD_SNAPSHOT_ARGUMENTS + [
            "name_must_match_pattern"
        ]
        assert instance.failures == expected_failures
        mock_in_scope_snapshots.assert_called_once()


def test_snapshot_names_match_pattern_failure_message():
    with (
        patch.object(SnapshotNamesMatchPattern, "failures"),
        patch.object(SnapshotNamesMatchPattern, "__call__"),
        patch(
            "checks.snapshot_checks.snapshot_names_match_pattern.object_name_does_not_match_pattern"
        ) as mock_message,
    ):
        pattern = r"^stg_"
        instance = SnapshotNamesMatchPattern(Namespace(name_must_match_pattern=pattern))
        mock_message.return_value = Mock()
        result = instance.failure_message
        mock_message.assert_called_with(
            objects=instance.failures,
            object_type="snapshot",
            name_must_match_pattern=pattern,
        )
        assert result is mock_message.return_value
