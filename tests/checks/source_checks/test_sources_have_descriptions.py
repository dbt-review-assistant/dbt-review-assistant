import sys
from argparse import Namespace
from typing import Iterable
from unittest.mock import Mock, PropertyMock, patch

import pytest

from checks.source_checks.sources_have_descriptions import SourcesHaveDescriptions
from utils.manifest_filter_conditions import ManifestFilterConditions
from utils.manifest_object.manifest_object import ManifestSource


@pytest.mark.parametrize(
    ids=[
        "two sources, both pass",
        "two sources, one fails",
    ],
    argnames=["sources", "expected_failures"],
    argvalues=[
        (
            [
                {
                    "unique_id": "test_source",
                    "description": "test_description",
                },
                {
                    "unique_id": "another_source",
                    "description": "test_description",
                },
            ],
            set(),
        ),
        (
            [
                {
                    "unique_id": "test_source",
                    "description": "test_description",
                },
                {
                    "unique_id": "another_source",
                    "description": "",
                },
            ],
            {"another_source"},
        ),
    ],
)
def test_sources_have_descriptions_perform_checks(
    sources: Iterable[dict[str, str]],
    expected_failures: set[str],
    tmpdir,
):
    with (
        patch.object(SourcesHaveDescriptions, "__call__"),
        patch.object(
            SourcesHaveDescriptions, "manifest", new_callable=PropertyMock
        ) as mock_manifest,
    ):
        mock_in_scope_sources = PropertyMock(
            return_value=[
                ManifestSource(source_data, ManifestFilterConditions())
                for source_data in sources
            ]
        )
        type(mock_manifest.return_value).in_scope_sources = mock_in_scope_sources
        instance = SourcesHaveDescriptions(Namespace())
        instance.perform_check()
        assert instance.check_name == "sources-have-descriptions"
        assert instance.additional_arguments == [
            "include_tags",
            "include_packages",
            "include_node_paths",
            "include_name_patterns",
            "exclude_tags",
            "exclude_packages",
            "exclude_node_paths",
            "exclude_name_patterns",
        ]
        assert instance.failures == expected_failures
        mock_in_scope_sources.assert_called_once()


def test_sources_have_descriptions_failure_message():
    with (
        patch.object(SourcesHaveDescriptions, "failures"),
        patch.object(SourcesHaveDescriptions, "__call__"),
        patch(
            "checks.source_checks.sources_have_descriptions.object_missing_attribute_message"
        ) as mock_object_missing_attribute_message,
    ):
        instance = SourcesHaveDescriptions(Namespace())
        mock_object_missing_attribute_message.return_value = Mock()
        result = instance.failure_message
        mock_object_missing_attribute_message.assert_called_with(
            missing_attributes=instance.failures,
            object_type="source",
            attribute_type="description",
        )
        assert result is mock_object_missing_attribute_message.return_value
