from argparse import Namespace
from typing import Iterable
from unittest.mock import Mock, PropertyMock, patch

import pytest

from checks.model_checks.model_column_names_must_match_pattern import (
    ModelColumnNamesMatchPattern,
)
from utils.check_abc import STANDARD_MODEL_ARGUMENTS
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
                    "columns": {
                        "test_column": {"name": "test_column_name"},
                        "another_column": {"name": "another_column"},
                    },
                },
                {
                    "name": "another_model",
                    "unique_id": "test_package.another_model",
                    "columns": {
                        "test_column": {"name": "test_column_name"},
                        "another_column": {"name": "another_column"},
                    },
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
                    "columns": {
                        "test_column": {"name": "test_column_name"},
                        "another_column": {"name": "another_column"},
                    },
                },
                {
                    "name": "another_model",
                    "unique_id": "test_package.another_model",
                    "columns": {
                        "test_column": {"name": "test_column_name"},
                        "one_more_column": {"name": "one_more_column"},
                    },
                },
            ],
            "(another_column|test_column_name)",
            {"test_package.another_model.one_more_column"},
        ),
    ],
)
def test_model_column_names_match_pattern_perform_checks(
    models: Iterable[dict[str, str]],
    pattern: str,
    expected_failures: set[str],
    tmpdir,
):
    with (
        patch.object(ModelColumnNamesMatchPattern, "__call__"),
        patch.object(
            ModelColumnNamesMatchPattern, "manifest", new_callable=PropertyMock
        ) as mock_manifest,
    ):
        columns = [
            column
            for model_data in models
            for column in ManifestModel(model_data).columns
        ]
        mock_in_scope_columns = PropertyMock(return_value=columns)
        type(mock_manifest.return_value).in_scope_model_columns = mock_in_scope_columns
        instance = ModelColumnNamesMatchPattern(Namespace())
        instance.args.name_must_match_pattern = pattern
        instance.perform_check()
        assert instance.check_name == "model-column-names-match-pattern"
        assert instance.additional_arguments == STANDARD_MODEL_ARGUMENTS + [
            "name_must_match_pattern",
        ]
        assert instance.failures == expected_failures
        mock_in_scope_columns.assert_called()


def test_model_column_names_match_pattern_failure_message():
    with (
        patch.object(ModelColumnNamesMatchPattern, "failures"),
        patch.object(ModelColumnNamesMatchPattern, "__call__"),
        patch(
            "checks.model_checks.model_column_names_must_match_pattern.object_name_does_not_match_pattern"
        ) as mock_object_name_does_not_match_pattern,
    ):
        instance = ModelColumnNamesMatchPattern(Namespace())
        pattern = "test_pattern"
        instance.args.name_must_match_pattern = pattern
        mock_object_name_does_not_match_pattern.return_value = Mock()
        result = instance.failure_message
        mock_object_name_does_not_match_pattern.assert_called_with(
            objects=instance.failures,
            object_type="model column",
            name_must_match_pattern=pattern,
        )
        assert result is mock_object_name_does_not_match_pattern.return_value
