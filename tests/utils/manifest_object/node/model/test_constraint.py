from unittest.mock import Mock
from contextlib import nullcontext as does_not_raise
import pytest
from _pytest.raises import RaisesExc

from utils.manifest_object.node.model.constraint import Constraint



@pytest.mark.parametrize(
    argnames=["data", "expected_raise", "expected_return"],
    ids=[
        "Valid type",
        "Invalid type",
    ],
    argvalues=[
        (
            {"type": "check"},
            does_not_raise(),
            "check",
        ),
        (
            {"type": "foo"},
            pytest.raises(ValueError, match="Unknown constraint type: foo\nValid constraints: check\nnot_null\nunique\nprimary_key\nforeign_key\ncustom"),
            None,
        ),
    ],
)
def test_constraint_type(data: dict, expected_raise: does_not_raise | RaisesExc[BaseException], expected_return: str | None):
    instance = Constraint(data)
    with expected_raise:
        assert instance.type == expected_return
