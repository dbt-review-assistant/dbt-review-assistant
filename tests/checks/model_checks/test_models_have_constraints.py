import sys
from typing import Iterable, Collection
from unittest.mock import patch, Mock

import pytest

from checks.model_checks.models_have_constraints import (
    ModelsHaveConstraints,
    model_has_constraints,
)


@pytest.mark.parametrize(
    ids=[
        "has required constraints",
        "has no constraints",
        "has constraints, required_constraints=None",
        "has no constraints, required_constraints=None",
    ],
    argnames=["model", "required_constraints", "expected_return"],
    argvalues=[
        (
            {"constraints": ["primary_key", "not_null"]},
            ["primary_key", "not_null"],
            True,
        ),
        (
            {"constraints": []},
            ["primary_key", "not_null"],
            False,
        ),
        (
            {"constraints": ["primary_key", "not_null"]},
            None,
            True,
        ),
        (
            {"constraints": []},
            None,
            False,
        ),
    ],
)
def test_model_has_constraints(
    model: dict, required_constraints: Collection[str], expected_return: bool
):
    assert model_has_constraints(model, required_constraints) is expected_return


@pytest.mark.parametrize(
    ids=[
        "two models with required constraints",
        "two models, one without required constraints, one with no constraints",
        "two models with constraints, argument constraints=None",
        "two models, one without constraints, argument constraints=None",
        "two models with required constraints, contract not enforced",
    ],
    argnames=["models", "constraints", "expected_failures"],
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
            set(),
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
            {"test_model", "another_model"},
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
            set(),
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
            {"another_model"},
        ),
        (
            [
                {
                    "unique_id": "test_model",
                    "constraints": ["primary_key", "not_null"],
                },
                {
                    "unique_id": "another_model",
                    "constraints": ["primary_key", "not_null"],
                },
            ],
            ["primary_key", "not_null"],
            {"test_model", "another_model"},
        ),
    ],
)
def test_models_have_constraints_perform_check(
    models: Iterable[dict[str, str]],
    constraints: Collection[str],
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
        instance.args.constraints = constraints
        instance.perform_check()
        assert instance.check_name == "models-have-constraints"
        assert instance.additional_arguments == [
            "constraints",
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
            "checks.model_checks.models_have_constraints.object_missing_attribute_message"
        ) as mock_object_missing_attribute_message,
    ):
        instance = ModelsHaveConstraints()
        instance.args.constraints = Mock()
        mock_object_missing_attribute_message.return_value = Mock()
        result = instance.failure_message
        mock_object_missing_attribute_message.assert_called_with(
            missing_attributes=instance.failures,
            object_type="model",
            attribute_type="constraint",
            expected_values=instance.args.constraints,
        )
        assert result is mock_object_missing_attribute_message.return_value
