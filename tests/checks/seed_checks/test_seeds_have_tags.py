from argparse import Namespace
from unittest.mock import Mock, PropertyMock, patch

import pytest

from checks.seed_checks.seeds_have_tags import SeedsHaveTags
from utils.check_abc import STANDARD_SEED_ARGUMENTS
from utils.manifest_object.node.node import ManifestSeed


@pytest.mark.parametrize(
    ids=[
        "seed has tags, no requirements",
        "seed has no tags, no requirements",
        "seed has required tags",
        "seed missing required tag",
    ],
    argnames=[
        "seeds",
        "must_have_all_tags_from",
        "must_have_any_tag_from",
        "expected_failures",
    ],
    argvalues=[
        (
            [{"unique_id": "test_seed", "tags": ["tag_1"]}],
            None,
            None,
            {},
        ),
        (
            [{"unique_id": "test_seed", "tags": []}],
            None,
            None,
            {"test_seed": set()},
        ),
        (
            [{"unique_id": "test_seed", "tags": ["tag_1", "tag_2"]}],
            {"tag_1", "tag_2"},
            None,
            {},
        ),
        (
            [{"unique_id": "test_seed", "tags": ["tag_1"]}],
            {"tag_1", "tag_2"},
            None,
            {"test_seed": {"tag_1"}},
        ),
    ],
)
def test_seeds_have_tags_perform_checks(
    seeds: list[dict],
    must_have_all_tags_from: set[str] | None,
    must_have_any_tag_from: set[str] | None,
    expected_failures: dict,
):
    with (
        patch.object(SeedsHaveTags, "__call__"),
        patch.object(
            SeedsHaveTags, "manifest", new_callable=PropertyMock
        ) as mock_manifest,
    ):
        mock_in_scope_seeds = PropertyMock(
            return_value=[ManifestSeed(s) for s in seeds]
        )
        type(mock_manifest.return_value).in_scope_seeds = mock_in_scope_seeds
        instance = SeedsHaveTags(Namespace())
        instance.args.must_have_all_tags_from = must_have_all_tags_from
        instance.args.must_have_any_tag_from = must_have_any_tag_from
        instance.perform_check()
        assert instance.check_name == "seeds-have-tags"
        assert instance.additional_arguments == STANDARD_SEED_ARGUMENTS + [
            "must_have_all_tags_from",
            "must_have_any_tag_from",
        ]
        assert instance.failures == expected_failures


def test_seeds_have_tags_failure_message():
    with (
        patch.object(SeedsHaveTags, "failures"),
        patch.object(SeedsHaveTags, "__call__"),
        patch(
            "checks.seed_checks.seeds_have_tags.object_missing_values_from_set_message"
        ) as mock_message,
    ):
        namespace = Namespace(
            must_have_all_tags_from=Mock(),
            must_have_any_tag_from=Mock(),
        )
        instance = SeedsHaveTags(namespace)
        mock_message.return_value = Mock()
        result = instance.failure_message
        mock_message.assert_called_with(
            objects=instance.failures,
            object_type="seed",
            attribute_type="tag",
            must_have_all_from=namespace.must_have_all_tags_from,
            must_have_any_from=namespace.must_have_any_tag_from,
        )
        assert result is mock_message.return_value
