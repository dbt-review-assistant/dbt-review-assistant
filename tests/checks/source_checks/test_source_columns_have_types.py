import sys
from typing import Iterable
from unittest.mock import Mock, PropertyMock, patch

import pytest

from checks.source_checks.source_columns_have_types import SourceColumnsHaveTypes
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
                    "columns": {
                        "column_1": {"name": "column_1", "data_type": "INT64"},
                        "column_2": {"name": "column_2", "data_type": "STRING"},
                    },
                },
                {
                    "unique_id": "another_source",
                    "columns": {
                        "column_1": {"name": "column_1", "data_type": "INT64"},
                        "column_2": {"name": "column_2", "data_type": "STRING"},
                    },
                },
            ],
            set(),
        ),
        (
            [
                {
                    "unique_id": "test_source",
                    "columns": {
                        "column_1": {"name": "column_1", "data_type": "INT64"},
                        "column_2": {"name": "column_2", "data_type": "STRING"},
                    },
                },
                {
                    "unique_id": "another_source",
                    "columns": {
                        "column_1": {"name": "column_1", "data_type": "INT64"},
                        "column_2": {"name": "column_2"},
                    },
                },
            ],
            {"another_source.column_2"},
        ),
    ],
)
def test_source_columns_have_types_perform_checks(
    sources: Iterable[dict[str, str]],
    expected_failures: set[str],
    tmpdir,
):
    with (
        patch.object(sys, "argv", return_value=[]),
        patch.object(SourceColumnsHaveTypes, "__call__"),
        patch.object(
            SourceColumnsHaveTypes, "manifest", new_callable=PropertyMock
        ) as mock_manifest,
    ):
        mock_in_scope_sources = PropertyMock(
            return_value=[
                ManifestSource(source_data, ManifestFilterConditions())
                for source_data in sources
            ]
        )
        type(mock_manifest.return_value).in_scope_sources = mock_in_scope_sources
        instance = SourceColumnsHaveTypes()
        instance.perform_check()
        assert instance.check_name == "source-columns-have-types"
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


def test_source_columns_have_descriptions_failure_message():
    with (
        patch.object(SourceColumnsHaveTypes, "failures"),
        patch.object(SourceColumnsHaveTypes, "parse_args"),
        patch.object(SourceColumnsHaveTypes, "__call__"),
        patch(
            "checks.source_checks.source_columns_have_types.object_missing_attribute_message"
        ) as mock_object_missing_attribute_message,
    ):
        instance = SourceColumnsHaveTypes()
        mock_object_missing_attribute_message.return_value = Mock()
        result = instance.failure_message
        mock_object_missing_attribute_message.assert_called_with(
            missing_attributes=instance.failures,
            object_type="source column",
            attribute_type="data_type",
        )
        assert result is mock_object_missing_attribute_message.return_value
