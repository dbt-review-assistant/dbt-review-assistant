from pathlib import Path
from unittest.mock import Mock

import pytest

from utils.manifest_object.manifest_object import (
    ConfigurableMixin,
    DataTestableMixin,
    HasColumnsMixin,
    HasPatchPathMixin,
    ManifestColumn,
    ManifestObject,
    dict_difference,
)
from utils.manifest_object.node.generic_test import GenericTest
from utils.manifest_object.node.model.constraint import Constraint
from utils.manifest_object.node.node import SingularTest


class ConcreteManifestObject(ManifestObject, HasPatchPathMixin):
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
    )
    assert instance.description == expected


def test_manifest_object_unique_id():
    instance = ConcreteManifestObject(
        data={"unique_id": "test_model"},
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
    )
    assert instance.package_name == expected


@pytest.mark.parametrize(
    argnames=["original_file_path", "expected"],
    ids=["has original_file_path", "None"],
    argvalues=[
        ("path/to/model.sql", Path("path/to/model.sql")),
        (None, None),
    ],
)
def test_manifest_object_original_file_path(original_file_path, expected):
    instance = ConcreteManifestObject(
        data={"original_file_path": original_file_path},
    )
    assert instance.original_file_path == expected


@pytest.mark.parametrize(
    argnames=[
        "data",
        "filepaths",
        "expected",
    ],
    ids=[
        "original_file_path one of included files",
        "patch_path one of included files",
        "Not included",
    ],
    argvalues=[
        (
            {"original_file_path": "path/to/model.sql"},
            [Path("path/to/model.sql"), Path("path/to/model.yml")],
            True,
        ),
        (
            {
                "patch_path": "test_package://path/to/model.yml",
                "package_name": "test_package",
            },
            [Path("path/to/model.sql"), Path("path/to/model.yml")],
            True,
        ),
        (
            {
                "original_file_path": "path/to/model.sql",
                "patch_path": "test_package://path/to/model.yml",
                "package_name": "test_package",
            },
            [Path("path/to/another_model.sql"), Path("path/to/another_model.yml")],
            False,
        ),
    ],
)
def test_manifest_object_is_included_by_original_or_patch_path(
    data: dict, filepaths: list[Path], expected: bool
):
    instance = ConcreteManifestObject(
        data=data,
    )
    assert instance.is_included_by_original_or_patch_path(filepaths) == expected


def test_manifest_object_name():
    instance = ConcreteManifestObject({"name": "test_macro"})
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
    )
    assert instance.name_matches_regex(regex_pattern) == expected


@pytest.mark.parametrize(
    argnames=["data", "expected_return"],
    ids=[
        "Has top-level meta",
        "No meta",
    ],
    argvalues=[
        (
            {"meta": {"test": 1}},
            {"test": 1},
        ),
        (
            {},
            {},
        ),
    ],
)
def test_manifest_object_meta(data: dict, expected_return: bool):
    instance = ConcreteManifestObject(data)
    assert instance.meta == expected_return


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
                ),
                "another_generic_test": GenericTest(
                    {"test_metadata": {"name": "another_generic_test"}},
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
                ),
                "another_generic_test": GenericTest(
                    {"test_metadata": {"name": "another_generic_test"}},
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
                ),
                "another_singular_test": SingularTest(
                    {"name": "another_singular_test"},
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
                ),
                "another_singular_test": SingularTest(
                    {"name": "another_singular_test"},
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
    instance = ConcreteDataTestableNode(data)
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
                ),
                "another_generic_test": GenericTest(
                    {"test_metadata": {"name": "another_generic_test"}},
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
                ),
                "another_generic_test": GenericTest(
                    {"test_metadata": {"name": "another_generic_test"}},
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
                ),
                "another_generic_test": GenericTest(
                    {"test_metadata": {"name": "another_generic_test"}},
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
                ),
                "another_generic_test": GenericTest(
                    {"test_metadata": {"name": "another_generic_test"}},
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
                ),
                "another_generic_test": GenericTest(
                    {"test_metadata": {"name": "another_generic_test"}},
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
                ),
                "another_generic_test": GenericTest(
                    {"test_metadata": {"name": "another_generic_test"}},
                ),
                "one_more_generic_test": GenericTest(
                    {"test_metadata": {"name": "one_more_generic_test"}},
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
                ),
                "another_generic_test": GenericTest(
                    {"test_metadata": {"name": "another_generic_test"}},
                ),
                "one_more_generic_test": GenericTest(
                    {"test_metadata": {"name": "one_more_generic_test"}},
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
                ),
                "another_generic_test": GenericTest(
                    {"test_metadata": {"name": "another_generic_test"}},
                ),
                "one_more_generic_test": GenericTest(
                    {"test_metadata": {"name": "one_more_generic_test"}},
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
    instance = ConcreteDataTestableNode(data)
    assert (
        instance.has_required_data_tests(
            manifest=mock_manifest,
            must_have_all_data_tests_from=must_have_all_data_tests_from,
            must_have_any_data_test_from=must_have_any_data_test_from,
        )
        is expected_return
    )


class ConcreteConfigurableNode(ConfigurableMixin, ManifestObject):
    pass


@pytest.mark.parametrize(
    argnames=["data", "expected_return"],
    ids=[
        "Has config",
        "No config",
        "Config is None",
    ],
    argvalues=[
        (
            {"config": {"enabled": True}},
            {"enabled": True},
        ),
        ({}, {}),
        ({"config": None}, {}),
    ],
)
def test_configurable_mixin_config(data: dict, expected_return: bool):
    instance = ConcreteConfigurableNode(data)
    assert instance.config == expected_return


@pytest.mark.parametrize(
    argnames=["data", "expected_return"],
    ids=[
        "Has meta under config",
        "Has top-level meta",
        "No meta",
    ],
    argvalues=[
        (
            {"config": {"meta": {"test": 1}}},
            {"test": 1},
        ),
        (
            {"meta": {"test": 1}},
            {"test": 1},
        ),
        (
            {},
            {},
        ),
    ],
)
def test_configurable_mixin_meta(data: dict, expected_return: bool):
    instance = ConcreteConfigurableNode(data)
    assert instance.meta == expected_return


@pytest.mark.parametrize(
    argnames=["data", "expected_return"],
    ids=[
        "Enabled",
        "Disabled",
    ],
    argvalues=[
        ({"config": {"enabled": True}}, True),
        ({"config": {"enabled": False}}, False),
    ],
)
def test_configurable_mixin_enabled(data: dict, expected_return: bool):
    instance = ConcreteConfigurableNode(data)
    assert instance.enabled == expected_return


@pytest.mark.parametrize(
    argnames=["data", "expected_config", "expected_return"],
    ids=[
        "Matched",
        "Not matched",
        "Not matched, nested",
    ],
    argvalues=[
        (
            {"config": {"materialized": "table"}},
            {"materialized": "table"},
            {},
        ),
        (
            {"config": {"materialized": "table"}},
            {"materialized": "view"},
            {
                "materialized": {
                    "right": "view",
                    "left": "table",
                },
            },
        ),
        (
            {"config": {"partition_by": {"granularity": "DAY"}}},
            {"partition_by": {"granularity": "MONTH"}},
            {
                "partition_by": {
                    "right": {"granularity": "MONTH"},
                    "left": {"granularity": "DAY"},
                },
            },
        ),
    ],
)
def test_dict_difference(
    data: dict,
    expected_config: dict,
    expected_return: bool,
):
    instance = ConcreteConfigurableNode(data)
    assert dict_difference(instance.config, expected_config) == expected_return
