from argparse import Namespace
from typing import Iterable
from unittest.mock import Mock, PropertyMock, patch

import pytest

from checks.snapshot_checks.snapshot_columns_have_descriptions import (
    SnapshotColumnsHaveDescriptions,
)
from utils.check_abc import STANDARD_SNAPSHOT_ARGUMENTS
from utils.manifest_object.manifest_object import ManifestColumn
from utils.manifest_object.node.node import ManifestSnapshot


@pytest.mark.parametrize(
    ids=[
        "two columns, both pass",
        "two columns, one fails",
    ],
    argnames=["columns", "expected_failures"],
    argvalues=[
        (
            [
                ManifestColumn(
                    {"name": "col_1", "description": "A description"},
                    ManifestSnapshot({"unique_id": "test_snapshot"}),
                ),
                ManifestColumn(
                    {"name": "col_2", "description": "Another description"},
                    ManifestSnapshot({"unique_id": "test_snapshot"}),
                ),
            ],
            set(),
        ),
        (
            [
                ManifestColumn(
                    {"name": "col_1", "description": "A description"},
                    ManifestSnapshot({"unique_id": "test_snapshot"}),
                ),
                ManifestColumn(
                    {"name": "col_2"},
                    ManifestSnapshot({"unique_id": "test_snapshot"}),
                ),
            ],
            {"test_snapshot.col_2"},
        ),
    ],
)
def test_snapshot_columns_have_descriptions_perform_checks(
    columns: Iterable[ManifestColumn],
    expected_failures: set[str],
):
    with (
        patch.object(SnapshotColumnsHaveDescriptions, "__call__"),
        patch.object(
            SnapshotColumnsHaveDescriptions, "manifest", new_callable=PropertyMock
        ) as mock_manifest,
    ):
        mock_in_scope_columns = PropertyMock(return_value=columns)
        type(
            mock_manifest.return_value
        ).in_scope_snapshot_columns = mock_in_scope_columns
        instance = SnapshotColumnsHaveDescriptions(Namespace())
        instance.perform_check()
        assert instance.check_name == "snapshot-columns-have-descriptions"
        assert instance.additional_arguments == STANDARD_SNAPSHOT_ARGUMENTS
        assert instance.failures == expected_failures
        mock_in_scope_columns.assert_called_once()


def test_snapshot_columns_have_descriptions_failure_message():
    with (
        patch.object(SnapshotColumnsHaveDescriptions, "failures"),
        patch.object(SnapshotColumnsHaveDescriptions, "__call__"),
        patch(
            "checks.snapshot_checks.snapshot_columns_have_descriptions.object_missing_attribute_message"
        ) as mock_message,
    ):
        instance = SnapshotColumnsHaveDescriptions(Namespace())
        mock_message.return_value = Mock()
        result = instance.failure_message
        mock_message.assert_called_with(
            missing_attributes=instance.failures,
            object_type="snapshot column",
            attribute_type="description",
        )
        assert result is mock_message.return_value
