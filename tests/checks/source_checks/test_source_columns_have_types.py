import sys
from typing import Iterable
from unittest.mock import patch, Mock

import pytest

from checks.source_checks.source_columns_have_types import SourceColumnsHaveTypes


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
                        "column_1": {"name": "column_1", "type": "INT64"},
                        "column_2": {"name": "column_2", "type": "STRING"},
                    },
                },
                {
                    "unique_id": "another_source",
                    "columns": {
                        "column_1": {"name": "column_1", "type": "INT64"},
                        "column_2": {"name": "column_2", "type": "STRING"},
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
                        "column_1": {"name": "column_1", "type": "INT64"},
                        "column_2": {"name": "column_2", "type": "STRING"},
                    },
                },
                {
                    "unique_id": "another_source",
                    "columns": {
                        "column_1": {"name": "column_1", "type": "INT64"},
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
        patch(
            "checks.source_checks.source_columns_have_types.get_sources_from_manifest",
            return_value=sources,
        ) as mock_get_sources_from_manifest,
    ):
        instance = SourceColumnsHaveTypes()
        instance.perform_check()
        assert instance.check_name == "source-columns-have-types"
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
            attribute_type="type",
        )
        assert result is mock_object_missing_attribute_message.return_value
