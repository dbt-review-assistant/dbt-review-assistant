from argparse import Namespace
from pathlib import Path
from typing import Collection
from unittest.mock import Mock, patch

import pytest

from checks.seed_checks.seeds_have_data_tests import SeedsHaveDataTests
from utils.check_abc import STANDARD_SEED_ARGUMENTS


@pytest.mark.parametrize(
    ids=[
        "two seeds, both pass",
        "two seeds, one fails",
        "one seed, passes no requirements",
        "one seed, fails no requirements",
    ],
    argnames=[
        "manifest_data",
        "must_have_all_data_tests_from",
        "must_have_any_data_test_from",
        "expected_failures",
    ],
    argvalues=[
        (
            {
                "sources": {},
                "nodes": {
                    "test_seed": {"unique_id": "test_seed", "resource_type": "seed"},
                    "another_seed": {
                        "unique_id": "another_seed",
                        "resource_type": "seed",
                    },
                    "unique_1": {
                        "resource_type": "test",
                        "test_metadata": {"name": "unique"},
                    },
                    "not_null_1": {
                        "resource_type": "test",
                        "test_metadata": {"name": "not_null"},
                    },
                    "unique_2": {
                        "resource_type": "test",
                        "test_metadata": {"name": "unique"},
                    },
                    "not_null_2": {
                        "resource_type": "test",
                        "test_metadata": {"name": "not_null"},
                    },
                },
                "child_map": {
                    "test_seed": ["unique_1", "not_null_1"],
                    "another_seed": ["unique_2", "not_null_2"],
                },
            },
            ["not_null", "unique"],
            None,
            {},
        ),
        (
            {
                "sources": {},
                "nodes": {
                    "test_seed": {"unique_id": "test_seed", "resource_type": "seed"},
                    "another_seed": {
                        "unique_id": "another_seed",
                        "resource_type": "seed",
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
                    "test_seed": ["unique_1", "not_null_1"],
                    "another_seed": [],
                },
            },
            ["not_null", "unique"],
            None,
            {"another_seed": set()},
        ),
        (
            {
                "sources": {},
                "nodes": {
                    "test_seed": {"unique_id": "test_seed", "resource_type": "seed"},
                    "unique_1": {
                        "resource_type": "test",
                        "test_metadata": {"name": "unique"},
                    },
                },
                "child_map": {"test_seed": ["unique_1"]},
            },
            None,
            None,
            {},
        ),
        (
            {
                "sources": {},
                "nodes": {
                    "test_seed": {"unique_id": "test_seed", "resource_type": "seed"},
                },
                "child_map": {"test_seed": []},
            },
            None,
            None,
            {"test_seed": set()},
        ),
    ],
)
def test_seeds_have_data_tests_perform_checks(
    manifest_data: dict,
    must_have_all_data_tests_from: Collection[str],
    must_have_any_data_test_from: Collection[str],
    expected_failures: dict,
):
    with (
        patch.object(SeedsHaveDataTests, "__call__"),
        patch("utils.artifact_data.get_json_artifact_data", return_value=manifest_data),
    ):
        instance = SeedsHaveDataTests(Namespace(manifest_dir=Path(".")))
        instance.args.must_have_all_data_tests_from = must_have_all_data_tests_from
        instance.args.must_have_any_data_test_from = must_have_any_data_test_from
        instance.perform_check()
        assert instance.check_name == "seeds-have-data-tests"
        assert instance.additional_arguments == STANDARD_SEED_ARGUMENTS + [
            "must_have_all_data_tests_from",
            "must_have_any_data_test_from",
        ]
        assert instance.failures == expected_failures


def test_seeds_have_data_tests_failure_message():
    with (
        patch.object(SeedsHaveDataTests, "failures"),
        patch.object(SeedsHaveDataTests, "__call__"),
        patch(
            "checks.seed_checks.seeds_have_data_tests.object_missing_values_from_set_message"
        ) as mock_message,
    ):
        namespace = Namespace(
            must_have_all_data_tests_from=Mock(),
            must_have_any_data_test_from=Mock(),
        )
        instance = SeedsHaveDataTests(namespace)
        mock_message.return_value = Mock()
        result = instance.failure_message
        mock_message.assert_called_with(
            objects=instance.failures,
            object_type="seed",
            attribute_type="data test",
            must_have_all_from=namespace.must_have_all_data_tests_from,
            must_have_any_from=namespace.must_have_any_data_test_from,
        )
        assert result is mock_message.return_value
