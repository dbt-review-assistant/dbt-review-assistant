from argparse import Namespace
from typing import Iterable
from unittest.mock import Mock, PropertyMock, patch

import pytest

from checks.source_checks.sources_have_columns import SourcesHaveColumns
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
                    "columns": {"test_column": {}},
                },
                {
                    "unique_id": "another_source",
                    "columns": {"test_column": {}},
                },
            ],
            set(),
        ),
        (
            [
                {
                    "unique_id": "test_source",
                    "columns": {"test_column": {}},
                },
                {
                    "unique_id": "another_source",
                },
            ],
            {"another_source"},
        ),
    ],
)
def test_sources_have_columns_perform_checks(
    sources: Iterable[dict[str, str]],
    expected_failures: set[str],
    tmpdir,
):
    with (
        patch.object(SourcesHaveColumns, "__call__"),
        patch.object(
            SourcesHaveColumns, "manifest", new_callable=PropertyMock
        ) as mock_manifest,
    ):
        mock_in_scope_sources = PropertyMock(
            return_value=[
                ManifestSource(source_data, ManifestFilterConditions())
                for source_data in sources
            ]
        )
        type(mock_manifest.return_value).in_scope_sources = mock_in_scope_sources
        instance = SourcesHaveColumns(Namespace())
        instance.perform_check()
        assert instance.check_name == "sources-have-columns"
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
        mock_in_scope_sources.assert_called()


def test_sources_have_columns_failure_message():
    with (
        patch.object(SourcesHaveColumns, "failures"),
        patch.object(SourcesHaveColumns, "__call__"),
        patch(
            "checks.source_checks.sources_have_columns.object_missing_attribute_message"
        ) as mock_object_missing_attribute_message,
    ):
        instance = SourcesHaveColumns(Namespace())
        mock_object_missing_attribute_message.return_value = Mock()
        result = instance.failure_message
        mock_object_missing_attribute_message.assert_called_with(
            missing_attributes=instance.failures,
            object_type="source",
            attribute_type="column",
        )
        assert result is mock_object_missing_attribute_message.return_value
