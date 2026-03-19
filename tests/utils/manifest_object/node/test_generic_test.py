import pytest

from utils.manifest_filter_conditions import ManifestFilterConditions
from utils.manifest_object.node.generic_test import GenericTest


@pytest.mark.parametrize(
    argnames=[
        "data",
        "expected_return",
    ],
    ids=[
        "Has generic test name",
        "Has test metadata but no generic test name",
        "Has no test metadata",
    ],
    argvalues=[
        (
            {
                "test_metadata": {"name": "not_null"},
            },
            "not_null",
        ),
        (
            {
                "test_metadata": {},
            },
            None,
        ),
        (
            {},
            None,
        ),
    ],
)
def test_generic_test_name(data: dict, expected_return: str | None):
    instance = GenericTest(data, filter_conditions=ManifestFilterConditions())
    assert instance.generic_test_name == expected_return
