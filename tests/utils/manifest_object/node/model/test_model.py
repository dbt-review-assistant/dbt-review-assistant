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
