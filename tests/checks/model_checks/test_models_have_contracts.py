import sys
from typing import Iterable
from unittest.mock import patch, Mock

import pytest

from checks.model_checks.models_have_contracts import (
    ModelsHaveContracts,
    model_has_contract_enforced,
)


@pytest.mark.parametrize(
    ids=[
        "has constract enforced",
        "has constract, not enforced",
        "has no contract",
        "contract is None",
    ],
    argnames=["model", "expected_return"],
    argvalues=[
        (
            {
                "config": {
                    "contract": {
                        "enforced": True,
                    }
                }
            },
            True,
        ),
        (
            {
                "config": {
                    "contract": {
                        "enforced": False,
                    }
                }
            },
            False,
        ),
        (
            {"config": {}},
            False,
        ),
        (
            {"config": {"contract": None}},
            False,
        ),
    ],
)
def test_model_has_contract_enforced(model: dict, expected_return: bool):
    assert model_has_contract_enforced(model) is expected_return


@pytest.mark.parametrize(
    ids=[
        "two models, both pass",
        "two models, one fails",
    ],
    argnames=["models", "expected_failures"],
    argvalues=[
        (
            [
                {
                    "unique_id": "test_model",
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
            set(),
        ),
        (
            [
                {
                    "unique_id": "test_model",
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
                            "enforced": False,
                        }
                    },
                },
            ],
            {"another_model"},
        ),
    ],
)
def test_models_have_contracts_perform_check(
    models: Iterable[dict[str, str]],
    expected_failures: set[str],
    tmpdir,
):
    with (
        patch.object(sys, "argv", return_value=[]),
        patch.object(ModelsHaveContracts, "__call__"),
        patch(
            "checks.model_checks.models_have_contracts.get_models_from_manifest",
            return_value=models,
        ) as mock_get_models_from_manifest,
    ):
        instance = ModelsHaveContracts()
        instance.perform_check()
        assert instance.check_name == "models-have-contracts"
        assert instance.additional_arguments == [
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


def test_models_have_contracts_failure_message():
    with (
        patch.object(ModelsHaveContracts, "failures"),
        patch.object(ModelsHaveContracts, "parse_args"),
        patch.object(ModelsHaveContracts, "__call__"),
        patch(
            "checks.model_checks.models_have_contracts.object_missing_attribute_message"
        ) as mock_object_missing_attribute_message,
    ):
        instance = ModelsHaveContracts()
        mock_object_missing_attribute_message.return_value = Mock()
        result = instance.failure_message
        mock_object_missing_attribute_message.assert_called_with(
            missing_attributes=instance.failures,
            object_type="model",
            attribute_type="contract",
        )
        assert result is mock_object_missing_attribute_message.return_value
