import sys
from typing import Collection
from unittest.mock import patch, Mock

import pytest

from checks.source_checks.sources_have_data_tests import SourcesHaveDataTests


@pytest.mark.parametrize(
    ids=[
        "two sources, both pass",
        "two sources, one fails",
        "two sources, both pass, data_tests=None",
        "two sources, one fails, data_tests=None",
    ],
    argnames=["manifest_data", "data_tests", "expected_failures"],
    argvalues=[
        (
            {
                "sources": {
                    "test_source": {
                        "unique_id": "test_source",
                        "resource_type": "source",
                    },
                    "another_source": {
                        "unique_id": "another_source",
                        "resource_type": "source",
                    },
                },
                "nodes": {
                    "unique_1": {
                        "resource_type": "test",
                        "test_metadata": {"name": "unique"},
                    },
                    "unique_2": {
                        "resource_type": "test",
                        "test_metadata": {"name": "unique"},
                    },
                    "not_null_1": {
                        "resource_type": "test",
                        "test_metadata": {"name": "not_null"},
                    },
                    "not_null_2": {
                        "resource_type": "test",
                        "test_metadata": {"name": "not_null"},
                    },
                },
                "child_map": {
                    "test_source": ["unique_1", "not_null_1"],
                    "another_source": ["unique_2", "not_null_2"],
                },
            },
            ["not_null", "unique"],
            set(),
        ),
        (
            {
                "sources": {
                    "test_source": {
                        "unique_id": "test_source",
                        "resource_type": "source",
                    },
                    "another_source": {
                        "unique_id": "another_source",
                        "resource_type": "source",
                    },
                },
                "nodes": {
                    "unique_1": {
                        "resource_type": "test",
                        "test_metadata": {"name": "unique"},
                    },
                    "not_null_1": {
                        "resource_type": "test",
                        "test_metadata": {"name": "not_null"},
                    },
                },
                "child_map": {
                    "test_source": ["unique_1", "not_null_1"],
                    "another_source": [],
                },
            },
            ["not_null", "unique"],
            {"another_source"},
        ),
        (
            {
                "sources": {
                    "test_source": {
                        "unique_id": "test_source",
                        "resource_type": "source",
                    },
                    "another_source": {
                        "unique_id": "another_source",
                        "resource_type": "source",
                    },
                },
                "nodes": {
                    "unique_1": {
                        "resource_type": "test",
                        "test_metadata": {"name": "unique"},
                    },
                    "unique_2": {
                        "resource_type": "test",
                        "test_metadata": {"name": "unique"},
                    },
                    "not_null_1": {
                        "resource_type": "test",
                        "test_metadata": {"name": "not_null"},
                    },
                    "not_null_2": {
                        "resource_type": "test",
                        "test_metadata": {"name": "not_null"},
                    },
                },
                "child_map": {
                    "test_source": ["unique_1", "not_null_1"],
                    "another_source": ["unique_2", "not_null_2"],
                },
            },
            None,
            set(),
        ),
        (
            {
                "sources": {
                    "test_source": {
                        "unique_id": "test_source",
                        "resource_type": "source",
                    },
                    "another_source": {
                        "unique_id": "another_source",
                        "resource_type": "source",
                    },
                },
                "nodes": {
                    "unique_1": {
                        "resource_type": "test",
                        "test_metadata": {"name": "unique"},
                    },
                    "unique_2": {
                        "resource_type": "test",
                        "test_metadata": {"name": "unique"},
                    },
                    "not_null_1": {
                        "resource_type": "test",
                        "test_metadata": {"name": "not_null"},
                    },
                },
                "child_map": {
                    "test_source": ["unique_1", "not_null_1"],
                    "another_source": ["unique_2"],
                },
            },
            ["not_null", "unique"],
            set(),
        ),
    ],
)
def test_sources_have_data_tests_perform_checks(
    manifest_data: dict[str, str],
    data_tests: Collection[str],
    expected_failures: set[str],
    tmpdir,
):
    with (
        patch.object(sys, "argv", return_value=[]),
        patch.object(SourcesHaveDataTests, "__call__"),
        patch(
            "checks.source_checks.sources_have_data_tests.get_json_artifact_data",
            return_value=manifest_data,
        ),
        patch(
            "utils.artifact_data.get_json_artifact_data",
            return_value=manifest_data,
        ),
    ):
        instance = SourcesHaveDataTests()
        instance.perform_check()
        instance.args.data_tests = data_tests
        assert instance.check_name == "sources-have-data-tests"
        assert instance.additional_arguments == [
            "data_tests",
            "include_tags",
            "include_packages",
            "include_node_paths",
            "exclude_tags",
            "exclude_packages",
            "exclude_node_paths",
        ]
        assert instance.failures == expected_failures


def test_sources_have_data_tests_failure_message():
    with (
        patch.object(SourcesHaveDataTests, "failures"),
        patch.object(SourcesHaveDataTests, "parse_args"),
        patch.object(SourcesHaveDataTests, "__call__"),
        patch(
            "checks.source_checks.sources_have_data_tests.object_missing_attribute_message"
        ) as mock_object_missing_attribute_message,
    ):
        instance = SourcesHaveDataTests()
        instance.args.data_tests = Mock()
        mock_object_missing_attribute_message.return_value = Mock()
        result = instance.failure_message
        mock_object_missing_attribute_message.assert_called_with(
            missing_attributes=instance.failures,
            object_type="source",
            attribute_type="data test",
            expected_values=instance.args.data_tests,
        )
        assert result is mock_object_missing_attribute_message.return_value
