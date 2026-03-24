import sys
from argparse import Namespace
from typing import Iterable
from unittest.mock import Mock, PropertyMock, patch

import pytest

from checks.model_checks.model_names_must_match_pattern import ModelNamesMatchPattern
from utils.manifest_filter_conditions import ManifestFilterConditions
from utils.manifest_object.node.model.model import ManifestModel


@pytest.mark.parametrize(
    ids=[
        "two models, both pass",
        "two models, one fails",
    ],
    argnames=["models", "pattern", "expected_failures"],
    argvalues=[
        (
            [
                {
                    "name": "test_model",
                    "unique_id": "test_package.test_model",
                },
                {
                    "name": "another_model",
                    "unique_id": "test_package.another_model",
                },
            ],
            "[a-z]",
            set(),
        ),
        (
            [
                {
                    "name": "test_model",
                    "unique_id": "test_package.test_model",
                },
                {
                    "name": "another_model",
                    "unique_id": "test_package.another_model",
                },
            ],
            "test_model",
            {"test_package.another_model"},
        ),
    ],
)
def test_model_names_match_pattern_perform_checks(
    models: Iterable[dict[str, str]],
    pattern: str,
    expected_failures: set[str],
    tmpdir,
):
    with (
        patch.object(ModelNamesMatchPattern, "__call__"),
        patch.object(
            ModelNamesMatchPattern, "manifest", new_callable=PropertyMock
        ) as mock_manifest,
    ):
        mock_in_scope_models = PropertyMock(
            return_value=[
                ManifestModel(model_data, ManifestFilterConditions())
                for model_data in models
            ]
        )
        type(mock_manifest.return_value).in_scope_models = mock_in_scope_models
        instance = ModelNamesMatchPattern(Namespace())
        instance.args.name_must_match_pattern = pattern
        instance.perform_check()
        assert instance.check_name == "model-names-match-pattern"
        assert instance.additional_arguments == [
            "include_materializations",
            "include_tags",
            "include_packages",
            "include_node_paths",
            "exclude_materializations",
            "exclude_tags",
            "exclude_packages",
            "exclude_node_paths",
            "name_must_match_pattern",
        ]
        assert instance.failures == expected_failures
        mock_in_scope_models.assert_called()


def test_model_names_match_pattern_failure_message():
    with (
        patch.object(ModelNamesMatchPattern, "failures"),
        patch.object(ModelNamesMatchPattern, "__call__"),
        patch(
            "checks.model_checks.model_names_must_match_pattern.object_name_does_not_match_pattern"
        ) as mock_object_name_does_not_match_pattern,
    ):
        instance = ModelNamesMatchPattern(Namespace())
        pattern = "test_pattern"
        instance.args.name_must_match_pattern = pattern
        mock_object_name_does_not_match_pattern.return_value = Mock()
        result = instance.failure_message
        mock_object_name_does_not_match_pattern.assert_called_with(
            objects=instance.failures,
            object_type="model",
            name_must_match_pattern=pattern,
        )
        assert result is mock_object_name_does_not_match_pattern.return_value
