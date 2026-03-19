from contextlib import nullcontext as does_not_raise

import pytest
from _pytest.raises import RaisesExc

from utils.manifest_filter_conditions import ManifestFilterConditions
from utils.manifest_object.node.generic_test import GenericTest


@pytest.mark.parametrize(
    argnames=["data", "expected_return", "expected_raise"],
    ids=[
        "Has generic test name",
        "Has test metadata but no generic test name",
        "Has no test metadata",
    ],
    argvalues=[
        (
            {
                "test_metadata": {"name": "not_null"},
                "unique_id": "test_model",
            },
            "not_null",
            does_not_raise(),
        ),
        (
            {
                "test_metadata": {},
                "unique_id": "test_model",
            },
            None,
            pytest.raises(AttributeError, match="has no generic test name."),
        ),
        (
            {
                "unique_id": "test_model",
            },
            None,
            pytest.raises(AttributeError, match="has no generic test name."),
        ),
    ],
)
def test_generic_test_name(
    data: dict,
    expected_return: str | None,
    expected_raise: does_not_raise | RaisesExc[BaseException],
):
    instance = GenericTest(data, filter_conditions=ManifestFilterConditions())
    with expected_raise:
        assert instance.name == expected_return


def test_generic_test_instance_name():
    instance = GenericTest(
        {"name": "not_null_my_model"}, filter_conditions=ManifestFilterConditions()
    )
    assert instance.instance_name == "not_null_my_model"
