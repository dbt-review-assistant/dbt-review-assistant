from argparse import Namespace
from typing import Iterable
from unittest.mock import Mock, PropertyMock, patch

import pytest

from checks.source_checks.sources_have_loader import SourcesHaveLoader
from utils.check_abc import STANDARD_SOURCE_ARGUMENTS
from utils.manifest_object.manifest_object import ManifestSource


@pytest.mark.parametrize(
    ids=[
        "two sources, both have loader",
        "two sources, one lacks loader",
    ],
    argnames=["sources", "expected_failures"],
    argvalues=[
        (
            [
                {"unique_id": "test_source", "loader": "fivetran"},
                {"unique_id": "another_source", "loader": "stitch"},
            ],
            set(),
        ),
        (
            [
                {"unique_id": "test_source", "loader": "fivetran"},
                {"unique_id": "another_source"},
            ],
            {"another_source"},
        ),
    ],
)
def test_sources_have_loader_perform_checks(
    sources: Iterable[dict],
    expected_failures: set[str],
):
    with (
        patch.object(SourcesHaveLoader, "__call__"),
        patch.object(
            SourcesHaveLoader, "manifest", new_callable=PropertyMock
        ) as mock_manifest,
    ):
        mock_in_scope_sources = PropertyMock(
            return_value=[ManifestSource(source_data) for source_data in sources]
        )
        type(mock_manifest.return_value).in_scope_sources = mock_in_scope_sources
        instance = SourcesHaveLoader(Namespace())
        instance.perform_check()
        assert instance.check_name == "sources-have-loader"
        assert instance.additional_arguments == STANDARD_SOURCE_ARGUMENTS
        assert instance.failures == expected_failures
        mock_in_scope_sources.assert_called_once()


def test_sources_have_loader_failure_message():
    with (
        patch.object(SourcesHaveLoader, "failures"),
        patch.object(SourcesHaveLoader, "__call__"),
        patch(
            "checks.source_checks.sources_have_loader.object_missing_attribute_message"
        ) as mock_message,
    ):
        instance = SourcesHaveLoader(Namespace())
        mock_message.return_value = Mock()
        result = instance.failure_message
        mock_message.assert_called_with(
            missing_attributes=instance.failures,
            object_type="source",
            attribute_type="loader",
        )
        assert result is mock_message.return_value
