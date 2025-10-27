import sys
from typing import Collection
from unittest.mock import patch, Mock

import pytest

from checks.model_checks.models_have_tags import ModelsHaveTags


@pytest.mark.parametrize(
    ids=[
        "model has both must_have_all_tags_from and must_have_any_tag_from",
        "model does not have must_have_any_tag_from",
        "model does not have must_have_all_tags_from",
        "model does not have any tags, no requirements",
        "model has tags, no requirements",
    ],
    argnames=[
        "models",
        "must_have_all_tags_from",
        "must_have_any_tag_from",
        "expected_failures",
    ],
    argvalues=[
        (
            [
                {
                    "unique_id": "test_model",
                    "tags": ["test_tag_1", "test_tag_2", "test_tag_3", "test_tag_4"],
                },
            ],
            {"test_tag_1", "test_tag_2"},
            {"test_tag_3", "test_tag_4"},
            {},
        ),
        (
            [
                {
                    "unique_id": "test_model",
                    "tags": ["test_tag_1", "test_tag_2"],
                },
            ],
            {"test_tag_1", "test_tag_2"},
            {"test_tag_3", "test_tag_4"},
            {"test_model": {"test_tag_1", "test_tag_2"}},
        ),
        (
            [
                {
                    "unique_id": "test_model",
                    "tags": ["test_tag_1", "test_tag_3"],
                },
            ],
            {"test_tag_1", "test_tag_2"},
            {"test_tag_3", "test_tag_4"},
            {"test_model": {"test_tag_1", "test_tag_3"}},
        ),
        (
            [
                {
                    "unique_id": "test_model",
                    "tags": [],
                },
            ],
            None,
            None,
            {"test_model": set()},
        ),
        (
            [
                {
                    "unique_id": "test_model",
                    "tags": ["test_tag_1"],
                },
            ],
            None,
            None,
            {},
        ),
    ],
)
def test_models_have_tags_perform_checks(
    models: dict,
    must_have_all_tags_from: set[str] | None,
    must_have_any_tag_from: set[str] | None,
    expected_failures: set[str],
    tmpdir,
):
    with (
        patch.object(sys, "argv", return_value=[]),
        patch.object(ModelsHaveTags, "__call__"),
        patch(
            "checks.model_checks.models_have_tags.get_models_from_manifest",
            return_value=models,
        ),
    ):
        instance = ModelsHaveTags()
        instance.args.must_have_all_tags_from = must_have_all_tags_from
        instance.args.must_have_any_tag_from = must_have_any_tag_from
        instance.perform_check()
        assert instance.check_name == "models-have-tags"
        assert instance.additional_arguments == [
            "must_have_all_tags_from",
            "must_have_any_tag_from",
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


def test_models_have_tags_failure_message():
    with (
        patch.object(ModelsHaveTags, "failures"),
        patch.object(ModelsHaveTags, "parse_args"),
        patch.object(ModelsHaveTags, "__call__"),
        patch(
            "checks.model_checks.models_have_tags.object_missing_values_from_set_message"
        ) as mock_object_missing_values_from_set_message,
    ):
        instance = ModelsHaveTags()
        instance.args.tags = Mock()
        mock_object_missing_values_from_set_message.return_value = Mock()
        result = instance.failure_message
        mock_object_missing_values_from_set_message.assert_called_with(
            objects=instance.failures,
            object_type="model",
            attribute_type="tag",
            must_have_all_from=instance.args.must_have_all_tags_from,
            must_have_any_from=instance.args.must_have_any_tag_from,
        )
        assert result is mock_object_missing_values_from_set_message.return_value
