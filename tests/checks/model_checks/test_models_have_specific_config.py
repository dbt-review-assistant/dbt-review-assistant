from argparse import Namespace
from typing import Any, Iterable
from unittest.mock import Mock, PropertyMock, patch

import pytest

from checks.model_checks.models_have_specific_config import ModelsHaveSpecificConfig
from utils.check_abc import STANDARD_MODEL_ARGUMENTS
from utils.manifest_object.node.model.model import ManifestModel


@pytest.mark.parametrize(
    ids=[
        "two models, both pass",
        "two models, one fails",
    ],
    argnames=["models", "expected_config", "expected_failures"],
    argvalues=[
        (
            [
                {
                    "unique_id": "test_model",
                    "config": {"materialized": "table"},
                },
                {
                    "unique_id": "another_model",
                    "config": {"materialized": "table"},
                },
            ],
            {"materialized": "table"},
            {},
        ),
        (
            [
                {
                    "unique_id": "test_model",
                    "config": {"materialized": "table"},
                },
                {
                    "unique_id": "another_model",
                    "config": {"materialized": "view"},
                },
            ],
            {"materialized": "table"},
            {"another_model": {"materialized": {"this": "view", "other": "table"}}},
        ),
    ],
)
def test_models_have_specific_config_perform_checks(
    models: Iterable[dict[str, str]],
    expected_config: dict[str, Any],
    expected_failures: set[str],
    tmpdir,
):
    with (
        patch.object(ModelsHaveSpecificConfig, "__call__"),
        patch.object(
            ModelsHaveSpecificConfig, "manifest", new_callable=PropertyMock
        ) as mock_manifest,
    ):
        mock_in_scope_models = PropertyMock(
            return_value=[ManifestModel(model_data) for model_data in models]
        )
        type(mock_manifest.return_value).in_scope_models = mock_in_scope_models
        instance = ModelsHaveSpecificConfig(
            Namespace(must_have_specific_config=expected_config)
        )
        instance.perform_check()
        assert instance.check_name == "models-have-specific-config"
        assert instance.additional_arguments == STANDARD_MODEL_ARGUMENTS + [
            "must_have_specific_config"
        ]
        assert instance.failures == expected_failures
        mock_in_scope_models.assert_called()


def test_models_have_properties_file_failure_message():
    with (
        patch.object(ModelsHaveSpecificConfig, "failures"),
        patch.object(ModelsHaveSpecificConfig, "__call__"),
        patch(
            "checks.model_checks.models_have_specific_config.dictionary_values_mismatch"
        ) as mock_dictionary_values_mismatch,
    ):
        instance = ModelsHaveSpecificConfig(Namespace())
        mock_dictionary_values_mismatch.return_value = Mock()
        result = instance.failure_message
        mock_dictionary_values_mismatch.assert_called_with(
            differences=instance.failures,
            object_type="model",
            dict_name="config",
        )
        assert result is mock_dictionary_values_mismatch.return_value
