from argparse import Namespace
from typing import Iterable
from unittest.mock import Mock, PropertyMock, patch

import pytest

from checks.seed_checks.seeds_have_descriptions import SeedsHaveDescriptions
from utils.check_abc import STANDARD_SEED_ARGUMENTS
from utils.manifest_object.node.node import ManifestSeed


@pytest.mark.parametrize(
    ids=[
        "two seeds, both pass",
        "two seeds, one fails",
    ],
    argnames=["seeds", "expected_failures"],
    argvalues=[
        (
            [
                {"unique_id": "test_seed", "description": "A test seed"},
                {"unique_id": "another_seed", "description": "Another seed"},
            ],
            set(),
        ),
        (
            [
                {"unique_id": "test_seed", "description": "A test seed"},
                {"unique_id": "another_seed", "description": ""},
            ],
            {"another_seed"},
        ),
    ],
)
def test_seeds_have_descriptions_perform_checks(
    seeds: Iterable[dict[str, str]],
    expected_failures: set[str],
):
    with (
        patch.object(SeedsHaveDescriptions, "__call__"),
        patch.object(
            SeedsHaveDescriptions, "manifest", new_callable=PropertyMock
        ) as mock_manifest,
    ):
        mock_in_scope_seeds = PropertyMock(
            return_value=[ManifestSeed(seed_data) for seed_data in seeds]
        )
        type(mock_manifest.return_value).in_scope_seeds = mock_in_scope_seeds
        instance = SeedsHaveDescriptions(Namespace())
        instance.perform_check()
        assert instance.check_name == "seeds-have-descriptions"
        assert instance.additional_arguments == STANDARD_SEED_ARGUMENTS
        assert instance.failures == expected_failures
        mock_in_scope_seeds.assert_called_once()


def test_seeds_have_descriptions_failure_message():
    with (
        patch.object(SeedsHaveDescriptions, "failures"),
        patch.object(SeedsHaveDescriptions, "__call__"),
        patch(
            "checks.seed_checks.seeds_have_descriptions.object_missing_attribute_message"
        ) as mock_object_missing_attribute_message,
    ):
        instance = SeedsHaveDescriptions(Namespace())
        mock_object_missing_attribute_message.return_value = Mock()
        result = instance.failure_message
        mock_object_missing_attribute_message.assert_called_with(
            missing_attributes=instance.failures,
            object_type="seed",
            attribute_type="description",
        )
        assert result is mock_object_missing_attribute_message.return_value
