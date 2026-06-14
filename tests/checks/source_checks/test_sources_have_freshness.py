from argparse import Namespace
from typing import Iterable
from unittest.mock import Mock, PropertyMock, patch

import pytest

from checks.source_checks.sources_have_freshness import SourcesHaveFreshness
from utils.check_abc import STANDARD_SOURCE_ARGUMENTS
from utils.manifest_object.manifest_object import ManifestSource


@pytest.mark.parametrize(
    ids=[
        "two sources, both have freshness",
        "two sources, one lacks freshness",
    ],
    argnames=["sources", "expected_failures"],
    argvalues=[
        (
            [
                {
                    "unique_id": "test_source",
                    "loaded_at_field": "updated_at",
                },
                {
                    "unique_id": "another_source",
                    "freshness": {
                        "warn_after": {"count": 24},
                        "error_after": {"count": None},
                    },
                },
            ],
            set(),
        ),
        (
            [
                {
                    "unique_id": "test_source",
                    "loaded_at_field": "updated_at",
                },
                {
                    "unique_id": "another_source",
                },
            ],
            {"another_source"},
        ),
    ],
)
def test_sources_have_freshness_perform_checks(
    sources: Iterable[dict],
    expected_failures: set[str],
):
    with (
        patch.object(SourcesHaveFreshness, "__call__"),
        patch.object(
            SourcesHaveFreshness, "manifest", new_callable=PropertyMock
        ) as mock_manifest,
    ):
        mock_in_scope_sources = PropertyMock(
            return_value=[ManifestSource(source_data) for source_data in sources]
        )
        type(mock_manifest.return_value).in_scope_sources = mock_in_scope_sources
        instance = SourcesHaveFreshness(Namespace())
        instance.perform_check()
        assert instance.check_name == "sources-have-freshness"
        assert instance.additional_arguments == STANDARD_SOURCE_ARGUMENTS
        assert instance.failures == expected_failures
        mock_in_scope_sources.assert_called_once()


def test_sources_have_freshness_failure_message():
    with (
        patch.object(SourcesHaveFreshness, "failures"),
        patch.object(SourcesHaveFreshness, "__call__"),
        patch(
            "checks.source_checks.sources_have_freshness.object_missing_attribute_message"
        ) as mock_object_missing_attribute_message,
    ):
        instance = SourcesHaveFreshness(Namespace())
        mock_object_missing_attribute_message.return_value = Mock()
        result = instance.failure_message
        mock_object_missing_attribute_message.assert_called_with(
            missing_attributes=instance.failures,
            object_type="source",
            attribute_type="freshness",
        )
        assert result is mock_object_missing_attribute_message.return_value
