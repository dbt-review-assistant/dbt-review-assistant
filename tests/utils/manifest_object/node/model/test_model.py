from unittest.mock import Mock

import pytest

from utils.manifest_filter_conditions import ManifestFilterConditions
from utils.manifest_object.node.generic_test import GenericTest
from utils.manifest_object.node.model.column import ManifestModelColumn
from utils.manifest_object.node.model.constraint import Constraint
from utils.manifest_object.node.model.contract import Contract
from utils.manifest_object.node.model.model import ManifestModel
from utils.manifest_object.node.node import SingularTest


@pytest.mark.parametrize(
    argnames=["data", "expected_return"],
    ids=[
        "2 columns",
        "No columns",
    ],
    argvalues=[
        (
            {
                "unique_id": "test_model",
                "columns": {
                    "column_1": {"data": "test_data"},
                    "column_2": {"data": "more_test_data"},
                },
            },
            {
                "test_model.column_1": ManifestModelColumn({"data": "test_data"}),
                "test_model.column_2": ManifestModelColumn({"data": "more_test_data"}),
            },
        ),
        (
            {"unique_id": "test_model", "columns": {}},
            {},
        ),
    ],
)
def test_manifest_model_columns(data: dict, expected_return: dict[str, ManifestModelColumn]):
    instance = ManifestModel(data, ManifestFilterConditions())
    assert instance.columns == expected_return


@pytest.mark.parametrize(
    argnames=["data", "expected_return"],
    ids=[
        "2 constraints",
        "No constraints",
    ],
    argvalues=[
        (
            {
                "unique_id": "test_model",
                "resource_type": "model",
                "constraints": [
                    {"type": "primary_key"},
                    {"type": "not_null"},
                ],
            },
            (Constraint({"type": "primary_key"}), Constraint({"type": "not_null"})),
        ),
        (
            {"unique_id": "test_model", "resource_type": "model", "constraints": []},
            tuple(),
        ),
    ],
)
def test_manifest_model_constraints(data: dict, expected_return: tuple[Constraint, ...]):
    instance = ManifestModel(data, ManifestFilterConditions())
    assert instance.constraints == expected_return


@pytest.mark.parametrize(
    argnames=["data", "expected_return"],
    ids=[
        "Contract",
        "No contract",
        "No config",
    ],
    argvalues=[
        (
            {
                "unique_id": "test_model",
                "resource_type": "model",
                "config": {"contract": {"data": "test_data"}},
            },
            Contract({"data": "test_data"}),
        ),
        (
            {
                "unique_id": "test_model",
                "resource_type": "model",
                "config": {"contract": {}},
            },
            None,
        ),
        (
            {
                "unique_id": "test_model",
                "resource_type": "model",
            },
            None,
        ),
    ],
)
def test_manifest_model_contract(data: dict, expected_return: tuple[Constraint, ...]):
    instance = ManifestModel(data, ManifestFilterConditions())
    assert instance.contract == expected_return


@pytest.mark.parametrize(
    argnames=["data", "expected_return"],
    ids=[
        "View",
        "Table",
        "No config",
        "No materialized key",
        "None",
    ],
    argvalues=[
        (
            {
                "unique_id": "test_model",
                "resource_type": "model",
                "config": {"materialized": "view"},
            },
            "view",
        ),
        (
            {
                "unique_id": "test_model",
                "resource_type": "model",
                "config": {"materialized": "table"},
            },
            "table",
        ),
        (
            {
                "unique_id": "test_model",
                "resource_type": "model",
            },
            None,
        ),
        (
            {
                "unique_id": "test_model",
                "resource_type": "model",
            },
            None,
        ),
        (
            {
                "unique_id": "test_model",
                "resource_type": "model",
                "config": {},
            },
            None,
        ),
    ],
)
def test_manifest_model_materialized(data: dict, expected_return: str):
    instance = ManifestModel(data, ManifestFilterConditions())
    assert instance.materialized == expected_return


@pytest.mark.parametrize(
    argnames=["data", "expected_return"],
    ids=[
        "Has contract enforced",
        "Has contract not enforced enforced",
        "Has contract but is ephemeral",
        "No contract",
    ],
    argvalues=[
        (
            {
                "unique_id": "test_model",
                "resource_type": "model",
                "config": {"contract": {"enforced": True}},
            },
            True,
        ),
        (
            {
                "unique_id": "test_model",
                "resource_type": "model",
                "config": {"contract": {"enforced": False}},
            },
            False,
        ),
        (
            {
                "unique_id": "test_model",
                "resource_type": "model",
                "config": {
                    "contract": {"enforced": False},
                    "materialized": "ephemeral",
                },
            },
            False,
        ),
        (
            {
                "unique_id": "test_model",
                "resource_type": "model",
            },
            False,
        ),
    ],
)
def test_manifest_model_has_contract(data: dict, expected_return: bool):
    instance = ManifestModel(data, ManifestFilterConditions())
    assert instance.has_contract is expected_return


@pytest.mark.parametrize(
    argnames=[
        "data",
        "include_materializations",
        "exclude_materializations",
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
                "config": {"materialized": "view"},
            },
            ["view"],
            None,
            True,
        ),
        (
            {
                "unique_id": "included-model",
                "resource_type": "model",
                "config": {"materialized": "view"},
            },
            ["table"],
            None,
            False,
        ),
        (
            {
                "unique_id": "included-model",
                "resource_type": "model",
                "config": {"materialized": "view"},
            },
            None,
            ["view"],
            False,
        ),
        (
            {
                "unique_id": "included-model",
                "resource_type": "model",
                "config": {"materialized": "view"},
            },
            None,
            ["table"],
            True,
        ),
        (
            {
                "unique_id": "included-model",
                "resource_type": "model",
                "config": {"materialized": "view"},
            },
            ["view"],
            ["table"],
            True,
        ),
        (
            {
                "unique_id": "included-model",
                "resource_type": "model",
                "config": {"materialized": "table"},
            },
            ["view"],
            ["table"],
            False,
        ),
        (
            {
                "unique_id": "included-model",
                "resource_type": "model",
                "config": {"materialized": "view"},
            },
            ["view"],
            ["view"],
            False,
        ),
    ],
)
def test_manifest_model_filter_nodes_by_materialization_type(
    data: dict,
    include_materializations: list[str],
    exclude_materializations: list[str],
    expected_return: bool,
):
    instance = ManifestModel(
        data,
        ManifestFilterConditions(
            _include_materializations=include_materializations,
            _exclude_materializations=exclude_materializations,
        ),
    )
    assert instance.filter_by_materialization_type is expected_return


@pytest.mark.parametrize(
    argnames=[
        "data",
        "must_have_all_constraints_from",
        "must_have_any_constraint_from",
        "expected_return",
    ],
    ids=[
        "Has two from 'must_have_all_constraints_from'",
        "Has one from 'must_have_all_constraints_from'",
        "Has two from 'must_have_any_constraint_from'",
        "Has one from 'must_have_any_constraint_from'",
        "Has none from 'must_have_any_constraint_from'",
        "Has two from 'must_have_all_constraints_from' and one from 'must_have_any_constraint_from'",
        "Has two from 'must_have_all_constraints_from' and none from 'must_have_any_constraint_from'",
        "Has one from 'must_have_all_constraints_from' and one from 'must_have_any_constraint_from'",
    ],
    argvalues=[
        (
            {
                "unique_id": "included-model",
                "resource_type": "model",
                "constraints": [
                    {"type": "not_null"},
                    {"type": "unique"},
                ],
            },
            ["not_null", "unique"],
            None,
            True,
        ),
        (
            {
                "unique_id": "included-model",
                "resource_type": "model",
                "constraints": [
                    {"type": "not_null"},
                ],
            },
            ["not_null", "unique"],
            None,
            False,
        ),
        (
            {
                "unique_id": "included-model",
                "resource_type": "model",
                "constraints": [
                    {"type": "not_null"},
                    {"type": "unique"},
                ],
            },
            None,
            ["not_null", "unique"],
            True,
        ),
        (
            {
                "unique_id": "included-model",
                "resource_type": "model",
                "constraints": [
                    {"type": "not_null"},
                ],
            },
            None,
            ["not_null", "unique"],
            True,
        ),
        (
            {
                "unique_id": "included-model",
                "resource_type": "model",
                "constraints": [],
            },
            None,
            ["not_null", "unique"],
            False,
        ),
        (
            {
                "unique_id": "included-model",
                "resource_type": "model",
                "constraints": [
                    {"type": "not_null"},
                    {"type": "unique"},
                    {"type": "check"},
                ],
            },
            ["not_null", "unique"],
            ["check", "primary_key"],
            True,
        ),
        (
            {
                "unique_id": "included-model",
                "resource_type": "model",
                "constraints": [
                    {"type": "not_null"},
                    {"type": "unique"},
                ],
            },
            ["not_null", "unique"],
            ["check", "primary_key"],
            False,
        ),
        (
            {
                "unique_id": "included-model",
                "resource_type": "model",
                "constraints": [
                    {"type": "not_null"},
                    {"type": "check"},
                ],
            },
            ["not_null", "unique"],
            ["check", "primary_key"],
            False,
        ),
    ],
)
def test_manifest_model_has_required_constraints(
    data: dict,
    must_have_all_constraints_from: list[str],
    must_have_any_constraint_from: list[str],
    expected_return: bool,
):
    instance = ManifestModel(data, ManifestFilterConditions())
    assert (
        instance.has_required_constraints(
            must_have_all_constraints_from=must_have_all_constraints_from,
            must_have_any_constraint_from=must_have_any_constraint_from,
        )
        is expected_return
    )


@pytest.mark.parametrize(
    argnames=[
        "data",
        "child_map",
        "unit_tests",
        "expected_return",
    ],
    ids=[
        "Has unit tests",
        "Has no unit tests",
    ],
    argvalues=[
        (
            {
                "unique_id": "test_model",
                "resource_type": "model",
            },
            {"test_model": ["test_unit_test"]},
            {"test_unit_test": {"test": True}},
            True,
        ),
        (
            {
                "unique_id": "test_model",
                "resource_type": "model",
            },
            {"test_model": []},
            {"test_unit_test": {"test": True}},
            False,
        ),
    ],
)
def test_manifest_model_has_unit_tests(
    data: dict,
    child_map: dict[str, list[str]],
    unit_tests: dict[str, dict],
    expected_return: bool,
):
    mock_manifest = Mock()
    mock_manifest.child_map = child_map
    mock_manifest.unit_tests = unit_tests
    instance = ManifestModel(data, ManifestFilterConditions())
    assert instance.has_unit_tests(manifest=mock_manifest) is expected_return


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
                "singular_test": SingularTest({"unique_id": "singular_test"},
                    filter_conditions=ManifestFilterConditions(),
                ),
                "another_singular_test": SingularTest({"unique_id": "another_singular_test"},
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
                "singular_test": SingularTest({"unique_id": "singular_test"},
                    filter_conditions=ManifestFilterConditions(),
                ),
                "another_singular_test": SingularTest({"unique_id": "another_singular_test"},
                    filter_conditions=ManifestFilterConditions(),
                ),
            },
            set(),
        ),
    ],
)
def test_manifest_model_get_data_tests(
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
    instance = ManifestModel(data, ManifestFilterConditions())
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
            {"test_model": ["test_generic_test", "another_generic_test", "one_more_generic_test"]},
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
                    {"unique_id": "singular_test"},
                    filter_conditions=ManifestFilterConditions(),
                ),
            },
            None,
            None,
            True,
        ),
    ],
)
def test_manifest_model_has_required_data_tests(
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
    instance = ManifestModel(data, ManifestFilterConditions())
    assert instance.has_required_data_tests(
        manifest=mock_manifest,
        must_have_all_data_tests_from=must_have_all_data_tests_from,
        must_have_any_data_test_from=must_have_any_data_test_from,
    ) is expected_return
