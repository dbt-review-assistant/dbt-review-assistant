from argparse import Namespace
from typing import Iterable
from unittest.mock import Mock, PropertyMock, patch

import pytest

from checks.source_checks.source_columns_have_descriptions import (
    SourceColumnsHaveDescriptions,
)
from utils.check_abc import STANDARD_SOURCE_ARGUMENTS
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
                        "column_1": {"name": "column_1", "description": "Column 1"},
                        "column_2": {"name": "column_2", "description": "Column 2"},
                    },
                },
                {
                    "unique_id": "another_source",
                    "columns": {
                        "column_1": {"name": "column_1", "description": "Column 1"},
                        "column_2": {"name": "column_2", "description": "Column 2"},
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
                        "column_1": {"name": "column_1", "description": "Column 1"},
                        "column_2": {"name": "column_2", "description": "Column 2"},
                    },
                },
                {
                    "unique_id": "another_source",
                    "columns": {
                        "column_1": {"name": "column_1", "description": "Column 1"},
                        "column_2": {"name": "column_2", "description": ""},
                    },
                },
            ],
            {"another_source.column_2"},
        ),
    ],
)
def test_source_columns_have_descriptions_perform_checks(
    sources: Iterable[dict[str, str]],
    expected_failures: set[str],
    tmpdir,
):
    with (
        patch.object(SourceColumnsHaveDescriptions, "__call__"),
        patch.object(
            SourceColumnsHaveDescriptions, "manifest", new_callable=PropertyMock
        ) as mock_manifest,
    ):
        mock_in_scope_sources = PropertyMock(
            return_value=[ManifestSource(source_data) for source_data in sources]
        )
        type(mock_manifest.return_value).in_scope_sources = mock_in_scope_sources
        instance = SourceColumnsHaveDescriptions(Namespace())
        instance.perform_check()
        assert instance.check_name == "source-columns-have-descriptions"
        assert instance.additional_arguments == STANDARD_SOURCE_ARGUMENTS
        assert instance.failures == expected_failures
        mock_in_scope_sources.assert_called_once()


def test_source_columns_have_descriptions_failure_message():
    with (
        patch.object(SourceColumnsHaveDescriptions, "failures"),
        patch.object(SourceColumnsHaveDescriptions, "__call__"),
        patch(
            "checks.source_checks.source_columns_have_descriptions.object_missing_attribute_message"
        ) as mock_object_missing_attribute_message,
    ):
        instance = SourceColumnsHaveDescriptions(Namespace())
        mock_object_missing_attribute_message.return_value = Mock()
        result = instance.failure_message
        mock_object_missing_attribute_message.assert_called_with(
            missing_attributes=instance.failures,
            object_type="source column",
            attribute_type="description",
        )
        assert result is mock_object_missing_attribute_message.return_value
