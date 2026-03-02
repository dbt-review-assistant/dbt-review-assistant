import pytest

from utils.manifest_filter_conditions import ManifestFilterConditions
from utils.manifest_object.manifest_object import ManifestObject


class ConcreteManifestObject(ManifestObject):
    pass


def test_concrete_manifest_object_init():
    instance = ConcreteManifestObject(
        data={"key": "value"},
        filter_conditions=ManifestFilterConditions(),
    )
    assert instance.data == {"key": "value"}
    assert instance.filter_conditions == ManifestFilterConditions()


@pytest.mark.parametrize(
    argnames=["other", "expected"],
    ids=["same data", "different data", "different type"],
    argvalues=[
        (
            ConcreteManifestObject(
                data={"key": "value"},
                filter_conditions=ManifestFilterConditions(),
            ),
            True,
        ),
        (
            ConcreteManifestObject(
                data={"key": "different_value"},
                filter_conditions=ManifestFilterConditions(),
            ),
            False,
        ),
        ("not a ConcreteManifestObject", False),
    ],
)
def test_concrete_manifest_object_eq(other, expected):
    instance = ConcreteManifestObject(
        data={"key": "value"},
        filter_conditions=ManifestFilterConditions(),
    )
    assert (instance == other) is expected


@pytest.mark.parametrize(
    argnames=["description", "expected"],
    ids=["has description", "None", "empty string"],
    argvalues=[
        ("test description", "test description"),
        (None, None),
        ("", ""),
    ],
)
def test_concrete_manifest_object_description(description, expected):
    instance = ConcreteManifestObject(
        data={"description": description},
        filter_conditions=ManifestFilterConditions(),
    )
    assert instance.description == expected


def test_concrete_manifest_object_unique_id():
    instance = ConcreteManifestObject(
        data={"unique_id": "test_model"},
        filter_conditions=ManifestFilterConditions(),
    )
    assert instance.unique_id == "test_model"


@pytest.mark.parametrize(
    argnames=["resource_type", "expected"],
    ids=["has resource_type", "None", "empty string"],
    argvalues=[
        ("test resource_type", "test resource_type"),
        (None, None),
        ("", ""),
    ],
)
def test_concrete_manifest_object_resource_type(resource_type, expected):
    instance = ConcreteManifestObject(
        data={"resource_type": resource_type},
        filter_conditions=ManifestFilterConditions(),
    )
    assert instance.resource_type == expected


@pytest.mark.parametrize(
    argnames=["package_name", "expected"],
    ids=["has package_name", "None", "empty string"],
    argvalues=[
        ("test package_name", "test package_name"),
        (None, None),
        ("", ""),
    ],
)
def test_concrete_manifest_object_package_name(package_name, expected):
    instance = ConcreteManifestObject(
        data={"package_name": package_name},
        filter_conditions=ManifestFilterConditions(),
    )
    assert instance.package_name == expected


@pytest.mark.parametrize(
    argnames=[
        "data",
        "include_packages",
        "exclude_packages",
        "expected_return",
    ],
    ids=[
        "Explicitly included",
        "Not explicitly included",
        "Explicitly excluded",
        "Not explicitly excluded",
        "Explicitly included, with exclude condition",
        "Explicitly excluded, with include condition",
    ],
    argvalues=[
        (
            {
                "unique_id": "included-model",
                "package_name": "test_dbt_package",
            },
            ["test_dbt_package"],
            None,
            True,
        ),
        (
            {
                "unique_id": "excluded-model",
                "package_name": "another_dbt_package",
            },
            ["test_dbt_package"],
            None,
            False,
        ),
        (
            {
                "unique_id": "included-model",
                "package_name": "test_dbt_package",
            },
            None,
            ["test_dbt_package"],
            False,
        ),
        (
            {
                "unique_id": "excluded-model",
                "package_name": "another_dbt_package",
            },
            None,
            ["test_dbt_package"],
            True,
        ),
        (
            {
                "unique_id": "included-model",
                "package_name": "test_dbt_package",
            },
            ["test_dbt_package"],
            ["different_dbt_package"],
            True,
        ),
        (
            {
                "unique_id": "included-model",
                "package_name": "test_dbt_package",
            },
            ["different_dbt_package"],
            ["test_dbt_package"],
            False,
        ),
    ],
)
def test_concrete_manifest_object_filter_by_package(
    data,
    include_packages,
    exclude_packages,
    expected_return,
):
    instance = ConcreteManifestObject(
        data=data,
        filter_conditions=ManifestFilterConditions(
            include_packages=include_packages,
            exclude_packages=exclude_packages,
        ),
    )
    assert instance.filter_by_package is expected_return
