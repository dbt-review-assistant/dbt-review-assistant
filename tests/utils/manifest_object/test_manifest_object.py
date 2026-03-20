from pathlib import Path
from unittest.mock import Mock, PropertyMock, patch

import pytest

from utils.manifest_filter_conditions import ManifestFilterConditions
from utils.manifest_object.manifest_object import (
    DataTestableMixin,
    HasColumnsMixin,
    ManifestColumn,
    ManifestObject,
)
from utils.manifest_object.node.generic_test import GenericTest
from utils.manifest_object.node.model.constraint import Constraint
from utils.manifest_object.node.node import SingularTest


class ConcreteManifestObject(ManifestObject):
    pass


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


def test_manifest_object_name():
    instance = ConcreteManifestObject(
        {"name": "test_macro"}, filter_conditions=ManifestFilterConditions()
    )
    assert instance.name == "test_macro"


@pytest.mark.parametrize(
    argnames=["data", "regex_pattern", "expected"],
    ids=[
        "match",
        "no match",
    ],
    argvalues=[
        (
            {"name": "my_test_model"},
            "my_[a-z]*_model",
            True,
        ),
        (
            {"name": "another_model"},
            "my_[a-z]*_model",
            False,
        ),
    ],
)
def test_manifest_object_name_matches_regex(
    data: dict, regex_pattern: str, expected: bool
):
    instance = ConcreteManifestObject(
        data=data,
        filter_conditions=ManifestFilterConditions(),
    )
    assert instance.name_matches_regex(regex_pattern) == expected


@pytest.mark.parametrize(
    argnames=[
        "data",
        "include_name_patterns",
        "exclude_name_patterns",
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
                "name": "included_model",
            },
            ["included_[a-z]*", "another_model"],
            None,
            True,
        ),
        (
            {
                "name": "excluded_model",
            },
            ["included_[a-z]*"],
            None,
            False,
        ),
        (
            {
                "name": "excluded_model",
            },
            None,
            ["excluded_[a-z]*", "another_model"],
            False,
        ),
        (
            {
                "name": "included_model",
            },
            None,
            ["excluded_[a-z]*"],
            True,
        ),
        (
            {
                "name": "included_model",
            },
            ["included_[a-z]*"],
            ["excluded_[a-z]*"],
            True,
        ),
        (
            {
                "name": "excluded_model",
            },
            ["included_[a-z]*"],
            ["excluded_[a-z]*"],
            False,
        ),
        (
            {
                "name": "excluded_model",
            },
            ["excluded_[a-z]*"],
            ["excluded_[a-z]*"],
            False,
        ),
    ],
)
def test_manifest_object_filter_by_name_pattern(
    data: dict,
    include_name_patterns: list[str],
    exclude_name_patterns: list[str],
    expected_return: bool,
):
    instance = ConcreteManifestObject(
        data=data,
        filter_conditions=ManifestFilterConditions(
            _include_name_patterns=include_name_patterns,
            _exclude_name_patterns=exclude_name_patterns,
        ),
    )
    assert instance.filter_by_name_pattern is expected_return


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
            _include_packages=include_packages,
            _exclude_packages=exclude_packages,
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
            _include_paths=include_paths,
            _exclude_paths=exclude_paths,
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
            _include_resource_types=include_resource_types,
            _exclude_resource_types=exclude_resource_types,
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
        ),
        patch.object(
            ConcreteManifestObject,
            "filter_by_package",
            new_callable=PropertyMock(return_value=filter_by_package),
        ),
        patch.object(
            ConcreteManifestObject,
            "filter_by_path",
            new_callable=PropertyMock(return_value=filter_by_path),
        ),
    ):
        instance = ConcreteManifestObject({}, ManifestFilterConditions())
        assert instance.is_in_scope is expected_return


def test_manifest_column_name():
    name = "test_column"
    instance = ManifestColumn({"name": name})
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
def test_manifest_column_data_type(data: dict, expected_return: str):
    instance = ManifestColumn(data)
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
def test_manifest_column_has_data_type(data: dict, expected_return: bool):
    instance = ManifestColumn(data)
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
            (Constraint({"type": "not_null"}), Constraint({"type": "unique"})),
        ),
        (
            {"constraints": []},
            tuple(),
        ),
    ],
)
def test_manifest_column_constraints(
    data: dict, expected_return: tuple[Constraint, ...]
):
    instance = ManifestColumn(data)
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
def test_manifest_column_description(data: dict, expected_return: str):
    instance = ManifestColumn(data)
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
def test_manifest_column_has_description(data: dict, expected_return: str):
    instance = ManifestColumn(data)
    assert instance.has_description == expected_return


class ConcreteHasColumnsMixin(HasColumnsMixin, ManifestObject):
    pass


@pytest.mark.parametrize(
    argnames=["data", "expected_return"],
    ids=[
        "Two columns",
        "Empty columns",
        "Missing columns key",
    ],
    argvalues=[
        (
            {
                "unique_id": "test_model",
                "columns": {
                    "column1": {"name": "column1", "data_type": "string"},
                    "column2": {"name": "column2", "data_type": "integer"},
                },
            },
            {
                "test_model.column1": ManifestColumn(
                    {"name": "column1", "data_type": "string"}
                ),
                "test_model.column2": ManifestColumn(
                    {"name": "column2", "data_type": "integer"}
                ),
            },
        ),
        (
            {"unique_id": "test_model", "columns": {}},
            {},
        ),
        (
            {
                "unique_id": "test_model",
            },
            {},
        ),
    ],
)
def test_has_columns_mixin_columns(
    data: dict, expected_return: dict[str, ManifestColumn]
):
    instance = ConcreteHasColumnsMixin(
        data=data,
        filter_conditions=ManifestFilterConditions(),
    )
    assert instance.columns == expected_return


class ConcreteDataTestableNode(DataTestableMixin, ManifestObject):
    pass


@pytest.mark.parametrize(
    argnames=[
        "data",
        "child_map",
        "generic_tests",
        "singular_tests",
        "expected_return",
    ],
    ids=[
        "Has generic tests",
        "Has no generic tests",
        "Has singular tests tests",
        "Has no tests tests",
    ],
    argvalues=[
        (
            {
                "unique_id": "test_model",
                "resource_type": "model",
            },
            {"test_model": ["test_generic_test", "another_generic_test"]},
            {
                "test_generic_test": GenericTest(
                    {"test_metadata": {"name": "test_generic_test"}},
                    filter_conditions=ManifestFilterConditions(),
                ),
                "another_generic_test": GenericTest(
                    {"test_metadata": {"name": "another_generic_test"}},
                    filter_conditions=ManifestFilterConditions(),
                ),
            },
            {},
            {"test_generic_test", "another_generic_test"},
        ),
        (
            {
                "unique_id": "test_model",
                "resource_type": "model",
            },
            {"test_model": []},
            {
                "test_generic_test": GenericTest(
                    {"test_metadata": {"name": "test_generic_test"}},
                    filter_conditions=ManifestFilterConditions(),
                ),
                "another_generic_test": GenericTest(
                    {"test_metadata": {"name": "another_generic_test"}},
                    filter_conditions=ManifestFilterConditions(),
                ),
            },
            {},
            set(),
        ),
        (
            {
                "unique_id": "test_model",
                "resource_type": "model",
            },
            {"test_model": ["singular_test", "another_singular_test"]},
            {},
            {
                "singular_test": SingularTest(
                    {"name": "singular_test"},
                    filter_conditions=ManifestFilterConditions(),
                ),
                "another_singular_test": SingularTest(
                    {"name": "another_singular_test"},
                    filter_conditions=ManifestFilterConditions(),
                ),
            },
            {"singular_test", "another_singular_test"},
        ),
        (
            {
                "unique_id": "test_model",
                "resource_type": "model",
            },
            {"test_model": []},
            {},
            {
                "singular_test": SingularTest(
                    {"name": "singular_test"},
                    filter_conditions=ManifestFilterConditions(),
                ),
                "another_singular_test": SingularTest(
                    {"name": "another_singular_test"},
                    filter_conditions=ManifestFilterConditions(),
                ),
            },
            set(),
        ),
    ],
)
def test_data_testable_mixin_get_data_tests(
    data: dict,
    child_map: dict[str, list[str]],
    generic_tests: dict[str, GenericTest],
    singular_tests: dict[str, SingularTest],
    expected_return: bool,
):
    mock_manifest = Mock()
    mock_manifest.child_map = child_map
    mock_manifest.generic_tests = generic_tests
    mock_manifest.singular_tests = singular_tests
    instance = ConcreteDataTestableNode(data, ManifestFilterConditions())
    assert instance.get_data_tests(manifest=mock_manifest) == expected_return


@pytest.mark.parametrize(
    argnames=[
        "data",
        "child_map",
        "generic_tests",
        "singular_tests",
        "must_have_all_data_tests_from",
        "must_have_any_data_test_from",
        "expected_return",
    ],
    ids=[
        "Has two from 'must_have_all_data_tests_from'",
        "Has one from 'must_have_all_data_tests_from'",
        "Has two from 'must_have_any_data_tests_from'",
        "Has one from 'must_have_any_data_tests_from'",
        "Has none from 'must_have_any_data_tests_from'",
        "Has two from 'must_have_all_data_tests_from' and one from 'must_have_any_data_tests_from'",
        "Has two from 'must_have_all_data_tests_from' and none from 'must_have_any_data_tests_from'",
        "Has one from 'must_have_all_data_tests_from' and one from 'must_have_any_data_tests_from'",
        "Has one singular test",
    ],
    argvalues=[
        (
            {
                "unique_id": "test_model",
                "resource_type": "model",
            },
            {"test_model": ["test_generic_test", "another_generic_test"]},
            {
                "test_generic_test": GenericTest(
                    {"test_metadata": {"name": "test_generic_test"}},
                    filter_conditions=ManifestFilterConditions(),
                ),
                "another_generic_test": GenericTest(
                    {"test_metadata": {"name": "another_generic_test"}},
                    filter_conditions=ManifestFilterConditions(),
                ),
            },
            {},
            ["test_generic_test", "another_generic_test"],
            None,
            True,
        ),
        (
            {
                "unique_id": "test_model",
                "resource_type": "model",
            },
            {"test_model": ["test_generic_test"]},
            {
                "test_generic_test": GenericTest(
                    {"test_metadata": {"name": "test_generic_test"}},
                    filter_conditions=ManifestFilterConditions(),
                ),
                "another_generic_test": GenericTest(
                    {"test_metadata": {"name": "another_generic_test"}},
                    filter_conditions=ManifestFilterConditions(),
                ),
            },
            {},
            ["test_generic_test", "another_generic_test"],
            None,
            False,
        ),
        (
            {
                "unique_id": "test_model",
                "resource_type": "model",
            },
            {"test_model": ["test_generic_test", "another_generic_test"]},
            {
                "test_generic_test": GenericTest(
                    {"test_metadata": {"name": "test_generic_test"}},
                    filter_conditions=ManifestFilterConditions(),
                ),
                "another_generic_test": GenericTest(
                    {"test_metadata": {"name": "another_generic_test"}},
                    filter_conditions=ManifestFilterConditions(),
                ),
            },
            {},
            None,
            ["test_generic_test", "another_generic_test"],
            True,
        ),
        (
            {
                "unique_id": "test_model",
                "resource_type": "model",
            },
            {"test_model": ["test_generic_test"]},
            {
                "test_generic_test": GenericTest(
                    {"test_metadata": {"name": "test_generic_test"}},
                    filter_conditions=ManifestFilterConditions(),
                ),
                "another_generic_test": GenericTest(
                    {"test_metadata": {"name": "another_generic_test"}},
                    filter_conditions=ManifestFilterConditions(),
                ),
            },
            {},
            None,
            ["test_generic_test", "another_generic_test"],
            True,
        ),
        (
            {
                "unique_id": "test_model",
                "resource_type": "model",
            },
            {"test_model": []},
            {
                "test_generic_test": GenericTest(
                    {"test_metadata": {"name": "test_generic_test"}},
                    filter_conditions=ManifestFilterConditions(),
                ),
                "another_generic_test": GenericTest(
                    {"test_metadata": {"name": "another_generic_test"}},
                    filter_conditions=ManifestFilterConditions(),
                ),
            },
            {},
            None,
            ["test_generic_test", "another_generic_test"],
            False,
        ),
        (
            {
                "unique_id": "test_model",
                "resource_type": "model",
            },
            {
                "test_model": [
                    "test_generic_test",
                    "another_generic_test",
                    "one_more_generic_test",
                ]
            },
            {
                "test_generic_test": GenericTest(
                    {"test_metadata": {"name": "test_generic_test"}},
                    filter_conditions=ManifestFilterConditions(),
                ),
                "another_generic_test": GenericTest(
                    {"test_metadata": {"name": "another_generic_test"}},
                    filter_conditions=ManifestFilterConditions(),
                ),
                "one_more_generic_test": GenericTest(
                    {"test_metadata": {"name": "one_more_generic_test"}},
                    filter_conditions=ManifestFilterConditions(),
                ),
            },
            {},
            ["test_generic_test", "another_generic_test"],
            ["one_more_generic_test"],
            True,
        ),
        (
            {
                "unique_id": "test_model",
                "resource_type": "model",
            },
            {"test_model": ["test_generic_test", "another_generic_test"]},
            {
                "test_generic_test": GenericTest(
                    {"test_metadata": {"name": "test_generic_test"}},
                    filter_conditions=ManifestFilterConditions(),
                ),
                "another_generic_test": GenericTest(
                    {"test_metadata": {"name": "another_generic_test"}},
                    filter_conditions=ManifestFilterConditions(),
                ),
                "one_more_generic_test": GenericTest(
                    {"test_metadata": {"name": "one_more_generic_test"}},
                    filter_conditions=ManifestFilterConditions(),
                ),
            },
            {},
            ["test_generic_test", "another_generic_test"],
            ["one_more_generic_test"],
            False,
        ),
        (
            {
                "unique_id": "test_model",
                "resource_type": "model",
            },
            {"test_model": ["test_generic_test", "one_more_generic_test"]},
            {
                "test_generic_test": GenericTest(
                    {"test_metadata": {"name": "test_generic_test"}},
                    filter_conditions=ManifestFilterConditions(),
                ),
                "another_generic_test": GenericTest(
                    {"test_metadata": {"name": "another_generic_test"}},
                    filter_conditions=ManifestFilterConditions(),
                ),
                "one_more_generic_test": GenericTest(
                    {"test_metadata": {"name": "one_more_generic_test"}},
                    filter_conditions=ManifestFilterConditions(),
                ),
            },
            {},
            ["test_generic_test", "another_generic_test"],
            ["one_more_generic_test"],
            False,
        ),
        (
            {
                "unique_id": "test_model",
                "resource_type": "model",
            },
            {"test_model": ["singular_test"]},
            {},
            {
                "singular_test": SingularTest(
                    {"name": "singular_test"},
                    filter_conditions=ManifestFilterConditions(),
                ),
            },
            None,
            None,
            True,
        ),
    ],
)
def test_data_testable_mixin_has_required_data_tests(
    data: dict,
    child_map: dict[str, list[str]],
    generic_tests: dict[str, GenericTest],
    singular_tests: dict[str, SingularTest],
    must_have_all_data_tests_from: list[str],
    must_have_any_data_test_from: list[str],
    expected_return: bool,
):
    mock_manifest = Mock()
    mock_manifest.child_map = child_map
    mock_manifest.generic_tests = generic_tests
    mock_manifest.singular_tests = singular_tests
    instance = ConcreteDataTestableNode(data, ManifestFilterConditions())
    assert (
        instance.has_required_data_tests(
            manifest=mock_manifest,
            must_have_all_data_tests_from=must_have_all_data_tests_from,
            must_have_any_data_test_from=must_have_any_data_test_from,
        )
        is expected_return
    )
