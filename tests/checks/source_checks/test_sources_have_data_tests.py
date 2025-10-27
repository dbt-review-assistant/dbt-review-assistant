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
        "one source, passes must_have_all_data_tests_from and must_have_any_data_test_from",
        "one source, fails must_have_all_data_tests_from and must_have_any_data_test_from",
        "one source, passes no requirements",
        "one source, fails no requirements",
    ],
    argnames=[
        "manifest_data",
        "must_have_all_data_tests_from",
        "must_have_any_data_test_from",
        "expected_failures",
    ],
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
            None,
            {},
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
            None,
            {"another_source": set()},
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
            None,
            {},
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
            None,
            {"another_source": {"unique"}},
        ),
        (
            {
                "sources": {
                    "test_source": {
                        "unique_id": "test_source",
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
                    "accepted_values_1": {
                        "resource_type": "test",
                        "test_metadata": {"name": "accepted_values"},
                    },
                },
                "child_map": {
                    "test_source": ["unique_1", "not_null_1", "accepted_values_1"],
                },
            },
            ["not_null", "unique"],
            ["accepted_values", "relationships"],
            {},
        ),
        (
            {
                "sources": {
                    "test_source": {
                        "unique_id": "test_source",
                        "resource_type": "source",
                    },
                },
                "nodes": {},
                "child_map": {
                    "test_source": [],
                },
            },
            ["not_null", "unique"],
            ["accepted_values", "relationships"],
            {"test_source": set()},
        ),
        (
            {
                "sources": {
                    "test_source": {
                        "unique_id": "test_source",
                        "resource_type": "source",
                    },
                },
                "nodes": {
                    "unique_1": {
                        "resource_type": "test",
                        "test_metadata": {"name": "unique"},
                    },
                },
                "child_map": {
                    "test_source": ["unique_1"],
                },
            },
            None,
            None,
            {},
        ),
        (
            {
                "sources": {
                    "test_source": {
                        "unique_id": "test_source",
                        "resource_type": "source",
                    },
                },
                "nodes": {},
                "child_map": {
                    "test_source": [],
                },
            },
            None,
            None,
            {"test_source": set()},
        ),
    ],
)
def test_sources_have_data_tests_perform_checks(
    manifest_data: dict[str, str],
    must_have_all_data_tests_from: Collection[str],
    must_have_any_data_test_from: Collection[str],
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
        instance.args.must_have_all_data_tests_from = must_have_all_data_tests_from
        instance.args.must_have_any_data_test_from = must_have_any_data_test_from
        instance.perform_check()
        assert instance.check_name == "sources-have-data-tests"
        assert instance.additional_arguments == [
            "must_have_all_data_tests_from",
            "must_have_any_data_test_from",
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
            "checks.source_checks.sources_have_data_tests.object_missing_values_from_set_message"
        ) as mock_object_missing_values_from_set_message,
    ):
        instance = SourcesHaveDataTests()
        instance.args.data_tests = Mock()
        mock_object_missing_values_from_set_message.return_value = Mock()
        result = instance.failure_message
        mock_object_missing_values_from_set_message.assert_called_with(
            objects=instance.failures,
            object_type="source",
            attribute_type="data test",
            must_have_all_from=instance.args.must_have_all_data_tests_from,
            must_have_any_from=instance.args.must_have_any_data_test_from,
        )
        assert result is mock_object_missing_values_from_set_message.return_value
