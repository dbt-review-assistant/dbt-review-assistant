import pytest

from utils.manifest_filter_conditions import ManifestFilterConditions
from utils.manifest_object.node.model.column import ManifestModelColumn
from utils.manifest_object.node.model.constraint import Constraint
from utils.manifest_object.node.model.contract import Contract
from utils.manifest_object.node.model.model import ManifestModel


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
                }
             },
            {
                "test_model.column_1": ManifestModelColumn({"data": "test_data"}),
                "test_model.column_2": ManifestModelColumn({"data": "more_test_data"}),
            },
        ),
        (
            {
                "unique_id": "test_model",
                "columns": {}
             },
            {},
        ),
    ],
)
def test_model_columns(data: dict, expected_return: dict[str, ManifestModelColumn]):
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
                ]
             },
            (Constraint({"type": "primary_key"}), Constraint({"type": "not_null"})),
        ),
        (
            {
                "unique_id": "test_model",
                "resource_type": "model",
                "constraints": []
             },
            tuple(),
        ),
    ],
)
def test_model_constraints(data: dict, expected_return: tuple[Constraint, ...]):
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
def test_model_contract(data: dict, expected_return: tuple[Constraint, ...]):
    instance = ManifestModel(data, ManifestFilterConditions())
    assert instance.contract == expected_return


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
def test_model_materialized(data: dict, expected_return: tuple[Constraint, ...]):
    instance = ManifestModel(data, ManifestFilterConditions())
    assert instance.materialized == expected_return
#
#
# @pytest.mark.parametrize(
#     argnames=[
#         "nodes",
#         "include_packages",
#         "exclude_packages",
#         "expected_return",
#     ],
#     ids=[
#         "One node in an included materialization",
#         "One node in an included materialization, one out of scope",
#         "Two nodes, both with different included materialization types",
#         "One included, one excluded, one omitted",
#         "No filter",
#     ],
#     argvalues=[
#         (
#             [
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "config": {"materialized": "table"},
#                     },
#                 ],
#                 ["table"],
#                 None,
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "config": {"materialized": "table"},
#                     },
#                 ],
#             ]
#         ),
#         (
#             [
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "config": {"materialized": "table"},
#                     },
#                     {
#                         "unique_id": "excluded-model",
#                         "config": {"materialized": "view"},
#                     },
#                 ],
#                 ["table"],
#                 None,
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "config": {"materialized": "table"},
#                     },
#                 ],
#             ]
#         ),
#         (
#             [
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "config": {"materialized": "table"},
#                     },
#                     {
#                         "unique_id": "another-included-model",
#                         "config": {"materialized": "view"},
#                     },
#                 ],
#                 ["table", "view"],
#                 None,
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "config": {"materialized": "table"},
#                     },
#                     {
#                         "unique_id": "another-included-model",
#                         "config": {"materialized": "view"},
#                     },
#                 ],
#             ]
#         ),
#         (
#             [
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "config": {"materialized": "table"},
#                     },
#                     {
#                         "unique_id": "excluded-model",
#                         "config": {"materialized": "view"},
#                     },
#                     {
#                         "unique_id": "omitted-model",
#                         "config": {"materialized": "ephemeral"},
#                     },
#                 ],
#                 ["table"],
#                 ["view"],
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "config": {"materialized": "table"},
#                     },
#                 ],
#             ]
#         ),
#         (
#             [
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "config": {"materialized": "table"},
#                     },
#                     {
#                         "unique_id": "another-included-model",
#                         "config": {"materialized": "view"},
#                     },
#                 ],
#                 None,
#                 None,
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "config": {"materialized": "table"},
#                     },
#                     {
#                         "unique_id": "another-included-model",
#                         "config": {"materialized": "view"},
#                     },
#                 ],
#             ]
#         ),
#     ],
# )
# def test_filter_models_by_materialization_type(
#     nodes: Iterable[dict],
#     include_packages: list[str],
#     exclude_packages: list[str],
#     expected_return: Generator[dict, None, None],
# ):
#     actual_return = filter_models_by_materialization_type(
#         iter(nodes), include_packages, exclude_packages
#     )
#     assert list(actual_return) == expected_return
