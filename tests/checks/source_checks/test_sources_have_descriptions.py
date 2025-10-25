import sys
from typing import Iterable
from unittest.mock import patch, Mock

import pytest

from checks.source_checks.sources_have_descriptions import SourcesHaveDescriptions


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
        patch.object(sys, "argv", return_value=[]),
        patch.object(SourcesHaveDescriptions, "__call__"),
        patch(
            "checks.source_checks.sources_have_descriptions.get_sources_from_manifest",
            return_value=sources,
        ) as mock_get_sources_from_manifest,
    ):
        instance = SourcesHaveDescriptions()
        instance.perform_check()
        assert instance.check_name == "sources-have-descriptions"
        assert instance.additional_arguments == [
            "include_tags",
            "include_packages",
            "include_node_paths",
            "exclude_tags",
            "exclude_packages",
            "exclude_node_paths",
        ]
        assert instance.failures == expected_failures
        mock_get_sources_from_manifest.assert_called_once_with(
            manifest_dir=instance.args.manifest_dir,
            filter_conditions=instance.filter_conditions,
        )


def test_sources_have_descriptions_failure_message():
    with (
        patch.object(SourcesHaveDescriptions, "failures"),
        patch.object(SourcesHaveDescriptions, "parse_args"),
        patch.object(SourcesHaveDescriptions, "__call__"),
        patch(
            "checks.source_checks.sources_have_descriptions.object_missing_attribute_message"
        ) as mock_object_missing_attribute_message,
    ):
        instance = SourcesHaveDescriptions()
        mock_object_missing_attribute_message.return_value = Mock()
        result = instance.failure_message
        mock_object_missing_attribute_message.assert_called_with(
            missing_attributes=instance.failures,
            object_type="source",
            attribute_type="description",
        )
        assert result is mock_object_missing_attribute_message.return_value
