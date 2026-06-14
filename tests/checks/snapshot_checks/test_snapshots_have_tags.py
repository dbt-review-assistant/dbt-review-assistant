from argparse import Namespace
from unittest.mock import Mock, PropertyMock, patch

import pytest

from checks.snapshot_checks.snapshots_have_tags import SnapshotsHaveTags
from utils.check_abc import STANDARD_SNAPSHOT_ARGUMENTS
from utils.manifest_object.node.node import ManifestSnapshot


@pytest.mark.parametrize(
    ids=[
        "snapshot has tags, no requirements",
        "snapshot has no tags, no requirements",
        "snapshot has required tags",
        "snapshot missing required tag",
    ],
    argnames=[
        "snapshots",
        "must_have_all_tags_from",
        "must_have_any_tag_from",
        "expected_failures",
    ],
    argvalues=[
        (
            [{"unique_id": "test_snapshot", "tags": ["tag_1"]}],
            None,
            None,
            {},
        ),
        (
            [{"unique_id": "test_snapshot", "tags": []}],
            None,
            None,
            {"test_snapshot": set()},
        ),
        (
            [{"unique_id": "test_snapshot", "tags": ["tag_1", "tag_2"]}],
            {"tag_1", "tag_2"},
            None,
            {},
        ),
        (
            [{"unique_id": "test_snapshot", "tags": ["tag_1"]}],
            {"tag_1", "tag_2"},
            None,
            {"test_snapshot": {"tag_1"}},
        ),
    ],
)
def test_snapshots_have_tags_perform_checks(
    snapshots: list[dict],
    must_have_all_tags_from: set[str] | None,
    must_have_any_tag_from: set[str] | None,
    expected_failures: dict,
):
    with (
        patch.object(SnapshotsHaveTags, "__call__"),
        patch.object(
            SnapshotsHaveTags, "manifest", new_callable=PropertyMock
        ) as mock_manifest,
    ):
        mock_in_scope_snapshots = PropertyMock(
            return_value=[ManifestSnapshot(s) for s in snapshots]
        )
        type(mock_manifest.return_value).in_scope_snapshots = mock_in_scope_snapshots
        instance = SnapshotsHaveTags(Namespace())
        instance.args.must_have_all_tags_from = must_have_all_tags_from
        instance.args.must_have_any_tag_from = must_have_any_tag_from
        instance.perform_check()
        assert instance.check_name == "snapshots-have-tags"
        assert instance.additional_arguments == STANDARD_SNAPSHOT_ARGUMENTS + [
            "must_have_all_tags_from",
            "must_have_any_tag_from",
        ]
        assert instance.failures == expected_failures


def test_snapshots_have_tags_failure_message():
    with (
        patch.object(SnapshotsHaveTags, "failures"),
        patch.object(SnapshotsHaveTags, "__call__"),
        patch(
            "checks.snapshot_checks.snapshots_have_tags.object_missing_values_from_set_message"
        ) as mock_message,
    ):
        namespace = Namespace(
            must_have_all_tags_from=Mock(),
            must_have_any_tag_from=Mock(),
        )
        instance = SnapshotsHaveTags(namespace)
        mock_message.return_value = Mock()
        result = instance.failure_message
        mock_message.assert_called_with(
            objects=instance.failures,
            object_type="snapshot",
            attribute_type="tag",
            must_have_all_from=namespace.must_have_all_tags_from,
            must_have_any_from=namespace.must_have_any_tag_from,
        )
        assert result is mock_message.return_value
