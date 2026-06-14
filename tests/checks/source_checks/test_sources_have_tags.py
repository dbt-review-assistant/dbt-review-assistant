from argparse import Namespace
from typing import Iterable
from unittest.mock import Mock, PropertyMock, patch

import pytest

from checks.source_checks.sources_have_tags import SourcesHaveTags
from utils.check_abc import STANDARD_SOURCE_ARGUMENTS
from utils.manifest_object.manifest_object import ManifestSource


@pytest.mark.parametrize(
    ids=[
        "source has tags, no requirements",
        "source has no tags, no requirements",
        "source has required tags",
        "source missing required tag",
    ],
    argnames=[
        "sources",
        "must_have_all_tags_from",
        "must_have_any_tag_from",
        "expected_failures",
    ],
    argvalues=[
        (
            [{"unique_id": "test_source", "tags": ["tag_1"]}],
            None,
            None,
            {},
        ),
        (
            [{"unique_id": "test_source", "tags": []}],
            None,
            None,
            {"test_source": set()},
        ),
        (
            [{"unique_id": "test_source", "tags": ["tag_1", "tag_2"]}],
            {"tag_1", "tag_2"},
            None,
            {},
        ),
        (
            [{"unique_id": "test_source", "tags": ["tag_1"]}],
            {"tag_1", "tag_2"},
            None,
            {"test_source": {"tag_1"}},
        ),
    ],
)
def test_sources_have_tags_perform_checks(
    sources: Iterable[dict],
    must_have_all_tags_from: set[str] | None,
    must_have_any_tag_from: set[str] | None,
    expected_failures: dict,
):
    with (
        patch.object(SourcesHaveTags, "__call__"),
        patch.object(
            SourcesHaveTags, "manifest", new_callable=PropertyMock
        ) as mock_manifest,
    ):
        mock_in_scope_sources = PropertyMock(
            return_value=[ManifestSource(s) for s in sources]
        )
        type(mock_manifest.return_value).in_scope_sources = mock_in_scope_sources
        instance = SourcesHaveTags(Namespace())
        instance.args.must_have_all_tags_from = must_have_all_tags_from
        instance.args.must_have_any_tag_from = must_have_any_tag_from
        instance.perform_check()
        assert instance.check_name == "sources-have-tags"
        assert instance.additional_arguments == STANDARD_SOURCE_ARGUMENTS + [
            "must_have_all_tags_from",
            "must_have_any_tag_from",
        ]
        assert instance.failures == expected_failures
        mock_in_scope_sources.assert_called_once()


def test_sources_have_tags_failure_message():
    with (
        patch.object(SourcesHaveTags, "failures"),
        patch.object(SourcesHaveTags, "__call__"),
        patch(
            "checks.source_checks.sources_have_tags.object_missing_values_from_set_message"
        ) as mock_message,
    ):
        namespace = Namespace(
            must_have_all_tags_from=Mock(),
            must_have_any_tag_from=Mock(),
        )
        instance = SourcesHaveTags(namespace)
        mock_message.return_value = Mock()
        result = instance.failure_message
        mock_message.assert_called_with(
            objects=instance.failures,
            object_type="source",
            attribute_type="tag",
            must_have_all_from=namespace.must_have_all_tags_from,
            must_have_any_from=namespace.must_have_any_tag_from,
        )
        assert result is mock_message.return_value
