from pathlib import Path
from typing import Iterable
from unittest.mock import patch, PropertyMock

import pytest

from utils.manifest_filter_conditions import ManifestFilterConditions
from utils.manifest_object.manifest_object import ManifestObject


class ConcreteManifestObject(ManifestObject):
    pass


def test_manifest_object_init():
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
def test_manifest_object_eq(other, expected):
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
def test_manifest_object_description(description, expected):
    instance = ConcreteManifestObject(
        data={"description": description},
        filter_conditions=ManifestFilterConditions(),
    )
    assert instance.description == expected


def test_manifest_object_unique_id():
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
def test_manifest_object_resource_type(resource_type, expected):
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
def test_manifest_object_package_name(package_name, expected):
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
        "Both explicitly included and explicitly excluded - exclude should take precedence",
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
                "unique_id": "excluded-model",
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
                "unique_id": "excluded-model",
                "package_name": "test_dbt_package",
            },
            ["different_dbt_package"],
            ["test_dbt_package"],
            False,
        ),
        (
            {
                "unique_id": "excluded-model",
                "package_name": "test_dbt_package",
            },
            ["test_dbt_package"],
            ["test_dbt_package"],
            False,
        ),
    ],
)
def test_manifest_object_filter_by_package(
    data: dict,
    include_packages: list[str],
    exclude_packages: list[str],
    expected_return: bool,
):
    instance = ConcreteManifestObject(
        data=data,
        filter_conditions=ManifestFilterConditions(
            include_packages=include_packages,
            exclude_packages=exclude_packages,
        ),
    )
    assert instance.filter_by_package is expected_return


@pytest.mark.parametrize(
    argnames=[
        "data",
        "include_paths",
        "exclude_paths",
        "expected_return",
    ],
    ids=[
        "Explicitly included",
        "Not explicitly included",
        "Explicitly excluded",
        "Not explicitly excluded",
        "Explicitly included, with exclude condition",
        "Explicitly excluded, with include condition",
        "Both explicitly included and explicitly excluded - exclude should take precedence",
        "Exact filepath match",
    ],
    argvalues=[
        (
            {
                "unique_id": "included-model",
                "original_file_path": "test/model/path",
            },
            [Path("test/model/")],
            None,
            True,
        ),
        (
            {
                "unique_id": "excluded-model",
                "original_file_path": "test/model/path",
            },
            [Path("test/model/subdir/")],
            None,
            False,
        ),
        (
            {
                "unique_id": "excluded-model",
                "original_file_path": "test/model/path",
            },
            None,
            [Path("test/model/")],
            False,
        ),
        (
            {
                "unique_id": "included-model",
                "original_file_path": "test/model/path",
            },
            None,
            [Path("test/model/subdir/")],
            True,
        ),
        (
            {
                "unique_id": "included-model",
                "original_file_path": "test/model/path",
            },
            [Path("test/model/")],
            [Path("test/model/subdir/")],
            True,
        ),
        (
            {
                "unique_id": "excluded-model",
                "original_file_path": "test/model/path",
            },
            [Path("test/model/subdir/")],
            [Path("test/model/")],
            False,
        ),
        (
            {
                "unique_id": "excluded-model",
                "original_file_path": "test/model/path",
            },
            [Path("test/model/")],
            [Path("test/model")],
            False,
        ),
        (
            {
                "unique_id": "included-model",
                "original_file_path": "test/model/path.sql",
            },
            [Path("test/model/path.sql")],
            None,
            True,
        ),
    ],
)
def test_manifest_object_filter_nodes_by_path(
    data: dict,
    include_paths: list[Path],
    exclude_paths: list[Path],
    expected_return: bool,
):
    instance = ConcreteManifestObject(
        data=data,
        filter_conditions=ManifestFilterConditions(
            include_paths=include_paths,
            exclude_paths=exclude_paths,
        ),
    )
    assert instance.filter_by_path is expected_return


@pytest.mark.parametrize(
    argnames=[
        "data",
        "include_resource_types",
        "exclude_resource_types",
        "expected_return",
    ],
    ids=[
        "Explicitly included",
        "Not explicitly included",
        "Explicitly excluded",
        "Not explicitly excluded",
        "Explicitly included, with exclude condition",
        "Explicitly excluded, with include condition",
        "Both explicitly included and explicitly excluded - exclude should take precedence",
    ],
    argvalues=[
        (
            {
                "unique_id": "included-model",
                "resource_type": "model",
            },
            ["model"],
            None,
            True,
        ),
        (
            {
                "unique_id": "excluded-model",
                "resource_type": "model",
            },
            ["seed"],
            None,
            False,
        ),
        (
            {
                "unique_id": "excluded-model",
                "resource_type": "model",
            },
            None,
            ["model"],
            False,
        ),
        (
            {
                "unique_id": "included-model",
                "resource_type": "model",
            },
            None,
            ["seed"],
            True,
        ),
        (
            {
                "unique_id": "included-model",
                "resource_type": "model",
            },
            ["model"],
            ["seed"],
            True,
        ),
        (
            {
                "unique_id": "excluded-model",
                "resource_type": "model",
            },
            ["seed"],
            ["model"],
            False,
        ),
        (
            {
                "unique_id": "excluded-model",
                "resource_type": "model",
            },
            ["model"],
            ["model"],
            False,
        ),
    ],
)
def test_manifest_object_filter_nodes_by_resource_type(
    data: dict,
    include_resource_types: list[str],
    exclude_resource_types: list[str],
    expected_return: bool,
):
    instance = ConcreteManifestObject(
        data=data,
        filter_conditions=ManifestFilterConditions(
            include_resource_types=include_resource_types,
            exclude_resource_types=exclude_resource_types,
        ),
    )
    assert instance.filter_by_resource_type is expected_return


@pytest.mark.parametrize(
    argnames=[
        "filter_by_resource_type",
        "filter_by_package",
        "filter_by_path",
        "expected_return",
    ],
    ids=[
        "All filters in scope",
        "No filters in scope",
        "Resource type in scope, others out of scope",
        "Package in scope, others out of scope",
        "Path in scope, others out of scope",
    ],
    argvalues=[
        (True, True, True, True),
        (False, False, False, False),
        (True, False, False, False),
        (False, True, False, False),
        (False, False, True, False),
    ],
)
def test_manifest_object_is_in_scope(
    filter_by_resource_type: bool,
    filter_by_package: bool,
    filter_by_path: bool,
    expected_return: bool,
):
    with (
        patch.object(
            ConcreteManifestObject,
            "filter_by_resource_type",
            new_callable=PropertyMock(return_value=filter_by_resource_type),
        ) as mock_filter_by_resource_type,
        patch.object(
            ConcreteManifestObject,
            "filter_by_package",
            new_callable=PropertyMock(return_value=filter_by_package),
        ) as mock_filter_by_package,
        patch.object(
            ConcreteManifestObject,
            "filter_by_path",
            new_callable=PropertyMock(return_value=filter_by_path),
        ) as mock_filter_by_path,
    ):
        instance = ConcreteManifestObject({}, ManifestFilterConditions())
        assert instance.is_in_scope is expected_return
