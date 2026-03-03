# @pytest.mark.parametrize(
#     argnames=[
#         "nodes",
#         "include_tags",
#         "exclude_tags",
#         "expected_return",
#     ],
#     ids=[
#         "Explicitly included",
#     ],
#     argvalues=[
#         (
#             [
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "tags": ["test_tag"],
#                     },
#                 ],
#                 ["test_tag"],
#                 None,
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "tags": ["test_tag"],
#                     },
#                 ],
#             ]
#         ),
#     ],
# )
# def test_concrete_manifest_object_filter_by_tags(
#     nodes: Iterable[dict],
#     include_tags: list[str],
#     exclude_tags: list[str],
#     expected_return: Generator[dict, None, None],
# ):
#     actual_return = filter_nodes_by_tag(iter(nodes), include_tags, exclude_tags)
#     assert list(actual_return) == expected_return
