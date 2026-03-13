import pytest

from utils.manifest_object.node.model.column import ManifestModelColumn
from utils.manifest_object.node.model.constraint import Constraint


def test_manifest_model_column_name():
    name = "test_column"
    instance = ManifestModelColumn({"name": name})
    assert instance.name == name


@pytest.mark.parametrize(
    argnames=["data", "expected_return"],
    ids=[
        "Has data type",
        "Has no data type",
    ],
    argvalues=[
        (
            {"data_type": "string"},
            "string",
        ),
        (
            {},
            None,
        ),
    ],
)
def test_manifest_model_column_data_type(data: dict, expected_return: str):
    instance = ManifestModelColumn(data)
    assert instance.data_type == expected_return


@pytest.mark.parametrize(
    argnames=["data", "expected_return"],
    ids=[
        "Has data type",
        "Has no data type",
    ],
    argvalues=[
        (
            {"data_type": "string"},
            True,
        ),
        (
            {},
            False,
        ),
    ],
)
def test_manifest_model_column_has_data_type(data: dict, expected_return: bool):
    instance = ManifestModelColumn(data)
    assert instance.has_data_type is expected_return


@pytest.mark.parametrize(
    argnames=["data", "expected_return"],
    ids=[
        "Has constraints",
        "Has no constraints",
    ],
    argvalues=[
        (
            {"constraints": [{"type": "not_null"}, {"type": "unique"}]},
            (Constraint({"type": "not_null"}),Constraint({"type": "unique"})),
        ),
        (
            {"constraints": []},
            tuple(),
        ),
    ],
)
def test_manifest_model_column_constraints(data: dict, expected_return: tuple[Constraint, ...]):
    instance = ManifestModelColumn(data)
    assert instance.constraints == expected_return


@pytest.mark.parametrize(
    argnames=["data", "expected_return"],
    ids=[
        "Has description",
        "Has no description",
    ],
    argvalues=[
        (
            {"description": "test description"},
            "test description",
        ),
        (
            {},
            None,
        ),
    ],
)
def test_manifest_model_column_description(data: dict, expected_return: str):
    instance = ManifestModelColumn(data)
    assert instance.description == expected_return


@pytest.mark.parametrize(
    argnames=["data", "expected_return"],
    ids=[
        "Has description",
        "Has no description",
    ],
    argvalues=[
        (
            {"description": "test description"},
            True,
        ),
        (
            {},
            False,
        ),
    ],
)
def test_manifest_model_column_has_description(data: dict, expected_return: str):
    instance = ManifestModelColumn(data)
    assert instance.has_description == expected_return
