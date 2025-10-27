import sys
from typing import Iterable, Collection
from unittest.mock import patch, Mock

import pytest

from checks.model_checks.models_have_constraints import ModelsHaveConstraints


@pytest.mark.parametrize(
    ids=[
        "two models with must_have_all_constraints_from",
        "two models, one without must_have_all_constraints_from, one with no constraints",
        "two models with constraints, argument constraints=None",
        "two models, one without constraints, argument must_have_all_constraints_from=None",
        "one model, passes must_have_all_constraints_from and must_have_any_constraint_from",
        "one model, fails must_have_all_constraints_from and must_have_any_constraint_from",
        "one model, passes no requirements",
        "one model, fails no requirements",
    ],
    argnames=[
        "models",
        "must_have_all_constraints_from",
        "must_have_any_constraint_from",
        "expected_failures",
    ],
    argvalues=[
        (
            [
                {
                    "unique_id": "test_model",
                    "constraints": ["primary_key", "not_null"],
                    "config": {
                        "contract": {
                            "enforced": True,
                        }
                    },
                },
                {
                    "unique_id": "another_model",
                    "constraints": ["primary_key", "not_null"],
                    "config": {
                        "contract": {
                            "enforced": True,
                        }
                    },
                },
            ],
            ["primary_key", "not_null"],
            None,
            {},
        ),
        (
            [
                {
                    "unique_id": "test_model",
                    "constraints": ["primary_key"],
                    "config": {
                        "contract": {
                            "enforced": True,
                        }
                    },
                },
                {
                    "unique_id": "another_model",
                    "config": {
                        "contract": {
                            "enforced": True,
                        }
                    },
                },
            ],
            ["primary_key", "not_null"],
            None,
            {"test_model": {"primary_key"}, "another_model": set()},
        ),
        (
            [
                {
                    "unique_id": "test_model",
                    "constraints": ["primary_key", "not_null"],
                    "config": {
                        "contract": {
                            "enforced": True,
                        }
                    },
                },
                {
                    "unique_id": "another_model",
                    "constraints": ["primary_key", "not_null"],
                    "config": {
                        "contract": {
                            "enforced": True,
                        }
                    },
                },
            ],
            None,
            None,
            {},
        ),
        (
            [
                {
                    "unique_id": "test_model",
                    "constraints": ["primary_key", "not_null"],
                    "config": {
                        "contract": {
                            "enforced": True,
                        }
                    },
                },
                {
                    "unique_id": "another_model",
                    "constraints": [],
                    "config": {
                        "contract": {
                            "enforced": True,
                        }
                    },
                },
            ],
            None,
            None,
            {"another_model": set()},
        ),
        (
            [
                {
                    "unique_id": "test_model",
                    "constraints": ["primary_key", "not_null", "unique"],
                    "config": {
                        "contract": {
                            "enforced": True,
                        }
                    },
                },
            ],
            ["primary_key", "not_null"],
            ["unique", "check"],
            {},
        ),
        (
            [
                {
                    "unique_id": "test_model",
                    "constraints": ["primary_key"],
                    "config": {
                        "contract": {
                            "enforced": True,
                        }
                    },
                },
            ],
            ["primary_key", "not_null"],
            ["unique", "check"],
            {"test_model": {"primary_key"}},
        ),
        (
            [
                {
                    "unique_id": "test_model",
                    "constraints": ["primary_key"],
                    "config": {
                        "contract": {
                            "enforced": True,
                        }
                    },
                },
            ],
            None,
            None,
            {},
        ),
        (
            [
                {
                    "unique_id": "test_model",
                    "constraints": [],
                    "config": {
                        "contract": {
                            "enforced": True,
                        }
                    },
                },
            ],
            None,
            None,
            {"test_model": set()},
        ),
    ],
)
def test_models_have_constraints_perform_check(
    models: Iterable[dict[str, str]],
    must_have_all_constraints_from: Collection[str],
    must_have_any_constraint_from: Collection[str],
    expected_failures: set[str],
    tmpdir,
):
    with (
        patch.object(sys, "argv", return_value=[]),
        patch.object(ModelsHaveConstraints, "__call__"),
        patch(
            "checks.model_checks.models_have_constraints.get_models_from_manifest",
            return_value=models,
        ) as mock_get_models_from_manifest,
    ):
        instance = ModelsHaveConstraints()
        instance.args.must_have_all_constraints_from = must_have_all_constraints_from
        instance.args.must_have_any_constraint_from = must_have_any_constraint_from
        instance.perform_check()
        assert instance.check_name == "models-have-constraints"
        assert instance.additional_arguments == [
            "must_have_all_constraints_from",
            "must_have_any_constraint_from",
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
        mock_get_models_from_manifest.assert_called_once_with(
            manifest_dir=instance.args.manifest_dir,
            filter_conditions=instance.filter_conditions,
        )


def test_models_have_constraints_failure_message():
    with (
        patch.object(ModelsHaveConstraints, "failures"),
        patch.object(ModelsHaveConstraints, "parse_args"),
        patch.object(ModelsHaveConstraints, "__call__"),
        patch(
            "checks.model_checks.models_have_constraints.object_missing_values_from_set_message"
        ) as mock_object_missing_values_from_set_message,
    ):
        instance = ModelsHaveConstraints()
        instance.args.constraints = Mock()
        mock_object_missing_values_from_set_message.return_value = Mock()
        result = instance.failure_message
        mock_object_missing_values_from_set_message.assert_called_with(
            objects=instance.failures,
            object_type="model",
            attribute_type="constraint",
            must_have_all_from=instance.args.must_have_all_constraints_from,
            must_have_any_from=instance.args.must_have_any_constraint_from,
        )
        assert result is mock_object_missing_values_from_set_message.return_value
