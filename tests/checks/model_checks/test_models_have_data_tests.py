import sys
from typing import Collection
from unittest.mock import patch, Mock

import pytest

from checks.model_checks.models_have_data_tests import ModelsHaveDataTests


@pytest.mark.parametrize(
    ids=[
        "two models, both pass must_have_all_data_tests_from",
        "two models, one fails must_have_all_data_tests_from",
        "two models, both pass, must_have_all_data_tests_from=None",
        "two models, one fails, must_have_all_data_tests_from=None",
        "one model, passes must_have_all_data_tests_from and must_have_any_data_test_from",
        "one model, fails must_have_all_data_tests_from and must_have_any_data_test_from",
        "one model, passes no requirements",
        "one model, fails no requirements",
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
                "nodes": {
                    "test_model": {
                        "unique_id": "test_model",
                        "resource_type": "model",
                    },
                    "another_model": {
                        "unique_id": "another_model",
                        "resource_type": "model",
                    },
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
                    "test_model": ["unique_1", "not_null_1"],
                    "another_model": ["unique_2", "not_null_2"],
                },
            },
            ["not_null", "unique"],
            None,
            {},
        ),
        (
            {
                "nodes": {
                    "test_model": {
                        "unique_id": "test_model",
                        "resource_type": "model",
                    },
                    "another_model": {
                        "unique_id": "another_model",
                        "resource_type": "model",
                    },
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
                    "test_model": ["unique_1", "not_null_1"],
                    "another_model": [],
                },
            },
            ["not_null", "unique"],
            None,
            {"another_model": set()},
        ),
        (
            {
                "nodes": {
                    "test_model": {
                        "unique_id": "test_model",
                        "resource_type": "model",
                    },
                    "another_model": {
                        "unique_id": "another_model",
                        "resource_type": "model",
                    },
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
                    "test_model": ["unique_1", "not_null_1"],
                    "another_model": ["unique_2", "not_null_2"],
                },
            },
            None,
            None,
            {},
        ),
        (
            {
                "nodes": {
                    "test_model": {
                        "unique_id": "test_model",
                        "resource_type": "model",
                    },
                    "another_model": {
                        "unique_id": "another_model",
                        "resource_type": "model",
                    },
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
                    "test_model": ["unique_1", "not_null_1"],
                    "another_model": ["unique_2"],
                },
            },
            ["not_null", "unique"],
            None,
            {"another_model": {"unique"}},
        ),
        (
            {
                "nodes": {
                    "test_model": {
                        "unique_id": "test_model",
                        "resource_type": "model",
                    },
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
                    "test_model": ["unique_1", "not_null_1", "accepted_values_1"],
                },
            },
            ["not_null", "unique"],
            ["accepted_values", "relationships"],
            {},
        ),
        (
            {
                "nodes": {
                    "test_model": {
                        "unique_id": "test_model",
                        "resource_type": "model",
                    },
                },
                "child_map": {
                    "test_model": [],
                },
            },
            ["not_null", "unique"],
            ["accepted_values", "relationships"],
            {"test_model": set()},
        ),
        (
            {
                "nodes": {
                    "test_model": {
                        "unique_id": "test_model",
                        "resource_type": "model",
                    },
                    "unique_1": {
                        "resource_type": "test",
                        "test_metadata": {"name": "unique"},
                    },
                },
                "child_map": {
                    "test_model": ["unique_1"],
                },
            },
            None,
            None,
            {},
        ),
        (
            {
                "nodes": {
                    "test_model": {
                        "unique_id": "test_model",
                        "resource_type": "model",
                    },
                },
                "child_map": {
                    "test_model": [],
                },
            },
            None,
            None,
            {"test_model": set()},
        ),
    ],
)
def test_models_have_data_tests_perform_checks(
    manifest_data: dict[str, str],
    must_have_all_data_tests_from: Collection[str],
    must_have_any_data_test_from: Collection[str],
    expected_failures: set[str],
    tmpdir,
):
    with (
        patch.object(sys, "argv", return_value=[]),
        patch.object(ModelsHaveDataTests, "__call__"),
        patch(
            "checks.model_checks.models_have_data_tests.get_json_artifact_data",
            return_value=manifest_data,
        ),
        patch(
            "utils.artifact_data.get_json_artifact_data",
            return_value=manifest_data,
        ),
    ):
        instance = ModelsHaveDataTests()
        instance.args.must_have_all_data_tests_from = must_have_all_data_tests_from
        instance.args.must_have_any_data_test_from = must_have_any_data_test_from
        instance.perform_check()
        assert instance.check_name == "models-have-data-tests"
        assert instance.additional_arguments == [
            "must_have_all_data_tests_from",
            "must_have_any_data_test_from",
            "include_materializations",
            "include_tags",
            "include_packages",
            "include_node_paths",
            "exclude_materializations",
            "exclude_tags",
            "exclude_packages",
            "exclude_node_paths",
        ]
        assert instance.failures == expected_failures


def test_models_have_data_tests_failure_message():
    with (
        patch.object(ModelsHaveDataTests, "failures"),
        patch.object(ModelsHaveDataTests, "parse_args"),
        patch.object(ModelsHaveDataTests, "__call__"),
        patch(
            "checks.model_checks.models_have_data_tests.object_missing_values_from_set_message"
        ) as mock_object_missing_values_from_set_message,
    ):
        instance = ModelsHaveDataTests()
        instance.args.data_tests = Mock()
        mock_object_missing_values_from_set_message.return_value = Mock()
        result = instance.failure_message
        mock_object_missing_values_from_set_message.assert_called_with(
            objects=instance.failures,
            object_type="model",
            attribute_type="data test",
            must_have_all_from=instance.args.must_have_all_data_tests_from,
            must_have_any_from=instance.args.must_have_any_data_test_from,
        )
        assert result is mock_object_missing_values_from_set_message.return_value
