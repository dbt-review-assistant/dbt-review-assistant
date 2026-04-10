from argparse import Namespace
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from checks.model_checks.models_have_unit_tests import ModelsHaveUnitTests
from utils.check_abc import STANDARD_MODEL_ARGUMENTS


@pytest.mark.parametrize(
    ids=[
        "two models, both pass",
        "two models, one fails",
    ],
    argnames=["manifest_data", "expected_failures"],
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
                },
                "child_map": {
                    "test_model": ["unit_test_1"],
                    "another_model": ["unit_test_2"],
                },
                "unit_tests": {
                    "unit_test_1": {"model": "test_model"},
                    "unit_test_2": {"model": "another_model"},
                },
            },
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
                },
                "child_map": {
                    "test_model": ["unit_test_1"],
                    "another_model": [],
                },
                "unit_tests": {
                    "unit_test_1": {"model": "test_model"},
                },
            },
            {"another_model"},
        ),
    ],
)
def test_models_have_unit_tests_perform_checks(
    manifest_data: dict[str, str],
    expected_failures: set[str],
    tmpdir,
):
    with (
        patch.object(ModelsHaveUnitTests, "__call__"),
        patch("utils.artifact_data.get_json_artifact_data", return_value=manifest_data),
    ):
        instance = ModelsHaveUnitTests(Namespace(manifest_dir=Path(".")))
        instance.perform_check()
        assert instance.check_name == "models-have-unit-tests"
        assert instance.additional_arguments == STANDARD_MODEL_ARGUMENTS
        assert instance.failures == expected_failures


def test_models_have_unit_tests_failure_message():
    with (
        patch.object(ModelsHaveUnitTests, "failures"),
        patch.object(ModelsHaveUnitTests, "__call__"),
        patch(
            "checks.model_checks.models_have_unit_tests.object_missing_attribute_message"
        ) as mock_object_missing_attribute_message,
    ):
        instance = ModelsHaveUnitTests(Namespace())
        mock_object_missing_attribute_message.return_value = Mock()
        result = instance.failure_message
        mock_object_missing_attribute_message.assert_called_with(
            missing_attributes=instance.failures,
            object_type="model",
            attribute_type="unit test",
        )
        assert result is mock_object_missing_attribute_message.return_value
