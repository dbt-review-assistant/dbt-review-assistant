from argparse import Namespace
from typing import Iterable
from unittest.mock import Mock, PropertyMock, patch

import pytest

from checks.model_checks.models_have_specific_materialization import (
    ModelsHaveSpecificMaterialization,
)
from utils.manifest_filter_conditions import ManifestFilterConditions
from utils.manifest_object.node.model.model import ManifestModel


@pytest.mark.parametrize(
    ids=[
        "two models, both pass",
        "two models, one fails",
    ],
    argnames=["models", "allowed_values", "expected_failures"],
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
            {"table", "view"},
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
                    "config": {"materialized": "ephemeral"},
                },
            ],
            {"table", "view"},
            {"another_model": "ephemeral"},
        ),
    ],
)
def test_models_have_columns_perform_checks(
    models: Iterable[dict[str, str]],
    allowed_values: set[str],
    expected_failures: set[str],
    tmpdir,
):
    with (
        patch.object(ModelsHaveSpecificMaterialization, "__call__"),
        patch.object(
            ModelsHaveSpecificMaterialization, "manifest", new_callable=PropertyMock
        ) as mock_manifest,
    ):
        mock_in_scope_models = PropertyMock(
            return_value=[
                ManifestModel(model_data, ManifestFilterConditions())
                for model_data in models
            ]
        )
        type(mock_manifest.return_value).in_scope_models = mock_in_scope_models
        instance = ModelsHaveSpecificMaterialization(
            Namespace(
                must_be_materialized_as_one_of=allowed_values,
            )
        )
        instance.perform_check()
        assert instance.check_name == "models-have-specific-materialization"
        assert instance.additional_arguments == [
            "include_tags",
            "include_packages",
            "include_node_paths",
            "include_name_patterns",
            "exclude_tags",
            "exclude_packages",
            "exclude_node_paths",
            "exclude_name_patterns",
            "must_be_materialized_as_one_of",
        ]
        assert instance.failures == expected_failures
        mock_in_scope_models.assert_called()


def test_models_have_columns_failure_message():
    with (
        patch.object(ModelsHaveSpecificMaterialization, "failures"),
        patch.object(ModelsHaveSpecificMaterialization, "__call__"),
        patch(
            "checks.model_checks.models_have_specific_materialization.object_attribute_value_not_in_set"
        ) as mock_object_attribute_value_not_in_set,
    ):
        mock_allowed_values = Mock()
        instance = ModelsHaveSpecificMaterialization(
            Namespace(must_be_materialized_as_one_of=mock_allowed_values)
        )
        mock_object_attribute_value_not_in_set.return_value = Mock()
        result = instance.failure_message
        mock_object_attribute_value_not_in_set.assert_called_with(
            objects=instance.failures,
            object_type="model",
            attribute_type="materialization",
            allowed_values=instance.args.must_be_materialized_as_one_of,
        )
        assert result is mock_object_attribute_value_not_in_set.return_value
