from unittest.mock import Mock

import pytest

from utils.manifest_object.node.model.contract import Contract


def test_contract_init():
    mock_data = Mock()
    instance = Contract(mock_data)
    assert instance.data is mock_data


@pytest.mark.parametrize(
    argnames=["data", "expected"],
    ids=[
        "enforced",
        "not enforced",
        "None",
        "Missing",
    ],
    argvalues=[
        (
            {"enforced": True},
            True,
        ),
        (
            {"enforced": False},
            False,
        ),
        (
            {"enforced": None},
            False,
        ),
        (
            {},
            False,
        ),
    ],
)
def test_contract_enforced(data: dict, expected: bool):
    instance = Contract(data)
    assert instance.enforced is expected
