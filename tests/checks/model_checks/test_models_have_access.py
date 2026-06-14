from argparse import Namespace
from typing import Iterable
from unittest.mock import Mock, PropertyMock, patch

import pytest

from checks.model_checks.models_have_access import ModelsHaveAccess
from utils.check_abc import STANDARD_MODEL_ARGUMENTS
from utils.manifest_object.node.model.model import ManifestModel


@pytest.mark.parametrize(
    ids=[
        "two models, both have allowed access",
        "two models, one has disallowed access",
        "model has no access set",
    ],
    argnames=["models", "allowed_values", "expected_failures"],
    argvalues=[
        (
            [
                {"unique_id": "test_model", "access": "public"},
                {"unique_id": "another_model", "access": "protected"},
            ],
            ["public", "protected"],
            {},
        ),
        (
            [
                {"unique_id": "test_model", "access": "public"},
                {"unique_id": "another_model", "access": "private"},
            ],
            ["public", "protected"],
            {"another_model": "private"},
        ),
        (
            [
                {"unique_id": "test_model"},
            ],
            ["public", "protected"],
            {"test_model": None},
        ),
    ],
)
def test_models_have_access_perform_checks(
    models: Iterable[dict],
    allowed_values: list[str],
    expected_failures: dict,
):
    with (
        patch.object(ModelsHaveAccess, "__call__"),
        patch.object(
            ModelsHaveAccess, "manifest", new_callable=PropertyMock
        ) as mock_manifest,
    ):
        mock_in_scope_models = PropertyMock(
            return_value=[ManifestModel(model_data) for model_data in models]
        )
        type(mock_manifest.return_value).in_scope_models = mock_in_scope_models
        instance = ModelsHaveAccess(
            Namespace(must_be_accessed_as_one_of=allowed_values)
        )
        instance.perform_check()
        assert instance.check_name == "models-have-access"
        assert instance.additional_arguments == STANDARD_MODEL_ARGUMENTS + [
            "must_be_accessed_as_one_of"
        ]
        assert instance.failures == expected_failures
        mock_in_scope_models.assert_called_once()


def test_models_have_access_failure_message():
    with (
        patch.object(ModelsHaveAccess, "failures"),
        patch.object(ModelsHaveAccess, "__call__"),
        patch(
            "checks.model_checks.models_have_access.object_attribute_value_not_in_set"
        ) as mock_message,
    ):
        mock_allowed_values = Mock()
        instance = ModelsHaveAccess(
            Namespace(must_be_accessed_as_one_of=mock_allowed_values)
        )
        mock_message.return_value = Mock()
        result = instance.failure_message
        mock_message.assert_called_with(
            objects=instance.failures,
            object_type="model",
            attribute_type="access",
            allowed_values=instance.args.must_be_accessed_as_one_of,
        )
        assert result is mock_message.return_value
