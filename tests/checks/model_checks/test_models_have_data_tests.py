import sys
from typing import Collection
from unittest.mock import patch, Mock

import pytest

from checks.model_checks.models_have_data_tests import ModelsHaveDataTests


@pytest.mark.parametrize(
    ids=[
        "two models, both pass",
        "two models, one fails",
        "two models, both pass, data_tests=None",
        "two models, one fails, data_tests=None",
    ],
    argnames=["manifest_data", "data_tests", "expected_failures"],
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
            set(),
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
            {"another_model"},
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
            set(),
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
            set(),
        ),
    ],
)
def test_models_have_data_tests_perform_checks(
    manifest_data: dict[str, str],
    data_tests: Collection[str],
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
        instance.perform_check()
        instance.args.data_tests = data_tests
        assert instance.check_name == "models-have-data-tests"
        assert instance.additional_arguments == [
            "data_tests",
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
            "checks.model_checks.models_have_data_tests.object_missing_attribute_message"
        ) as mock_object_missing_attribute_message,
    ):
        instance = ModelsHaveDataTests()
        instance.args.data_tests = Mock()
        mock_object_missing_attribute_message.return_value = Mock()
        result = instance.failure_message
        mock_object_missing_attribute_message.assert_called_with(
            missing_attributes=instance.failures,
            object_type="model",
            attribute_type="data test",
            expected_values=instance.args.data_tests,
        )
        assert result is mock_object_missing_attribute_message.return_value
