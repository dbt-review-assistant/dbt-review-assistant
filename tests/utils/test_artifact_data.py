import json
from pathlib import Path
from contextlib import nullcontext as does_not_raise
from typing import Iterable, Generator
from unittest.mock import patch

from utils.artifact_data import (
    get_json_artifact_data,
    filter_nodes_by_package,
    filter_nodes_by_tag,
    filter_models_by_materialization_type,
    filter_nodes_by_resource_type,
    get_macros_from_manifest,
    get_sources_from_manifest,
    get_nodes_from_manifest,
    get_models_from_manifest,
    ManifestFilterConditions,
    filter_nodes_by_path,
)
from utils.console_formatting import colour_message, ConsoleEmphasis
import pytest


@pytest.mark.parametrize(
    argnames=["artifact_path", "exists", "contents", "expected_raise"],
    ids=["File exists", "File does not exist"],
    argvalues=[
        (
            Path("path/to/manifest.json"),
            True,
            {"test": "ok"},
            does_not_raise(),
        ),
        (
            Path("path/to/manifest.json"),
            False,
            {"test": "ok"},
            pytest.raises(FileNotFoundError),
        ),
    ],
)
def test_get_json_artifact_data(
    artifact_path: Path,
    exists: bool,
    contents: dict,
    expected_raise,
    tmpdir,
):
    tmp_artifact_path = Path(tmpdir) / artifact_path
    if exists:
        tmp_artifact_path.parent.mkdir(parents=True, exist_ok=True)
        with open(tmp_artifact_path, "w") as f:
            json.dump(contents, f)
    with expected_raise:
        result = get_json_artifact_data(tmp_artifact_path)
        assert result == contents


@pytest.mark.parametrize(
    argnames=[
        "nodes",
        "include_packages",
        "exclude_packages",
        "expected_return",
    ],
    ids=[
        "One node included",
        "One node included, one omitted",
        "Package not found in manifest",
        "Two nodes, both with different included packages",
        "One included, one excluded, one omitted",
        "No filter",
    ],
    argvalues=[
        (
            [
                [
                    {
                        "unique_id": "included-model",
                        "package_name": "test_dbt_package",
                    },
                ],
                ["test_dbt_package"],
                None,
                [
                    {
                        "unique_id": "included-model",
                        "package_name": "test_dbt_package",
                    },
                ],
            ]
        ),
        (
            [
                [
                    {
                        "unique_id": "included-model",
                        "package_name": "test_dbt_package",
                    },
                    {
                        "unique_id": "excluded-model",
                        "package_name": "another_dbt_package",
                    },
                ],
                ["test_dbt_package"],
                None,
                [
                    {
                        "unique_id": "included-model",
                        "package_name": "test_dbt_package",
                    },
                ],
            ]
        ),
        (
            [
                [
                    {
                        "unique_id": "excluded-model",
                        "package_name": "test_dbt_package",
                        "description": None,
                    },
                ],
                ["another_dbt_package"],
                None,
                [],
            ]
        ),
        (
            [
                [
                    {
                        "unique_id": "included-model",
                        "package_name": "test_dbt_package",
                    },
                    {
                        "unique_id": "another-included-model",
                        "package_name": "another_dbt_package",
                    },
                ],
                ["test_dbt_package", "another_dbt_package"],
                None,
                [
                    {
                        "unique_id": "included-model",
                        "package_name": "test_dbt_package",
                    },
                    {
                        "unique_id": "another-included-model",
                        "package_name": "another_dbt_package",
                    },
                ],
            ]
        ),
        (
            [
                [
                    {
                        "unique_id": "included-model",
                        "package_name": "test_dbt_package",
                    },
                    {
                        "unique_id": "excluded-model",
                        "package_name": "another_dbt_package",
                    },
                    {
                        "unique_id": "omitted-model",
                        "package_name": "one_more_dbt_package",
                    },
                ],
                ["test_dbt_package"],
                ["another_dbt_package"],
                [
                    {
                        "unique_id": "included-model",
                        "package_name": "test_dbt_package",
                    },
                ],
            ]
        ),
        (
            [
                [
                    {
                        "unique_id": "included-model",
                        "package_name": "test_dbt_package",
                    },
                    {
                        "unique_id": "another-included-model",
                        "package_name": "another_dbt_package",
                    },
                    {
                        "unique_id": "one-more-model",
                        "package_name": "one_more_dbt_package",
                    },
                ],
                None,
                None,
                [
                    {
                        "unique_id": "included-model",
                        "package_name": "test_dbt_package",
                    },
                    {
                        "unique_id": "another-included-model",
                        "package_name": "another_dbt_package",
                    },
                    {
                        "unique_id": "one-more-model",
                        "package_name": "one_more_dbt_package",
                    },
                ],
            ]
        ),
    ],
)
def test_filter_nodes_by_package(
    nodes: Iterable[dict],
    include_packages: list[str],
    exclude_packages: list[str],
    expected_return: Generator[dict, None, None],
):
    actual_return = filter_nodes_by_package(
        iter(nodes), include_packages, exclude_packages
    )
    assert list(actual_return) == expected_return


@pytest.mark.parametrize(
    argnames=[
        "nodes",
        "include_tags",
        "exclude_tags",
        "expected_return",
    ],
    ids=[
        "One node with an included tag",
        "One node with an included tag, and one node with an excluded tag",
        "One node with an included tag and an excluded tag",
        "Two nodes, both with different included tags",
        "One node with an included tag and an excluded tag",
        "No filters",
        "One node included, tags under config key",
        "One node having all included tags",
        "One node having all but one included tags",
    ],
    argvalues=[
        (
            [
                [
                    {
                        "unique_id": "included-model",
                        "tags": ["test_tag"],
                    },
                ],
                ["test_tag"],
                None,
                [
                    {
                        "unique_id": "included-model",
                        "tags": ["test_tag"],
                    },
                ],
            ]
        ),
        (
            [
                [
                    {
                        "unique_id": "included-model",
                        "tags": ["test_tag"],
                    },
                    {
                        "unique_id": "excluded-model",
                        "tags": ["another_tag"],
                    },
                ],
                ["test_tag"],
                None,
                [
                    {
                        "unique_id": "included-model",
                        "tags": ["test_tag"],
                    },
                ],
            ]
        ),
        (
            [
                [
                    {
                        "unique_id": "included-model",
                        "tags": ["test_tag", "another_tag"],
                    },
                ],
                ["test_tag"],
                None,
                [
                    {
                        "unique_id": "included-model",
                        "tags": ["test_tag", "another_tag"],
                    },
                ],
            ]
        ),
        (
            [
                [
                    {
                        "unique_id": "included-model",
                        "tags": ["test_tag"],
                    },
                    {
                        "unique_id": "another-included-model",
                        "tags": ["another_tag"],
                    },
                ],
                ["test_tag", "another_tag"],
                None,
                [
                    {
                        "unique_id": "included-model",
                        "tags": ["test_tag"],
                    },
                    {
                        "unique_id": "another-included-model",
                        "tags": ["another_tag"],
                    },
                ],
            ]
        ),
        (
            [
                [
                    {
                        "unique_id": "excluded-model",
                        "tags": ["test_tag", "another_tag"],
                    },
                ],
                ["test_tag"],
                ["another_tag"],
                [],
            ]
        ),
        (
            [
                [
                    {
                        "unique_id": "included-model",
                        "tags": ["test_tag"],
                    },
                    {
                        "unique_id": "another-included-model",
                        "tags": ["another_tag"],
                    },
                ],
                None,
                None,
                [
                    {
                        "unique_id": "included-model",
                        "tags": ["test_tag"],
                    },
                    {
                        "unique_id": "another-included-model",
                        "tags": ["another_tag"],
                    },
                ],
            ]
        ),
        (
            [
                [
                    {
                        "unique_id": "included-model",
                        "config": {"tags": ["test_tag"]},
                    },
                ],
                ["test_tag"],
                None,
                [
                    {
                        "unique_id": "included-model",
                        "config": {"tags": ["test_tag"]},
                    },
                ],
            ]
        ),
        (
            [
                [
                    {
                        "unique_id": "included-model",
                        "tags": ["tag1", "tag2", "tag3"],
                    },
                ],
                ["tag1", "tag2", "tag3"],
                None,
                [
                    {
                        "unique_id": "included-model",
                        "tags": ["tag1", "tag2", "tag3"],
                    },
                ],
            ]
        ),
        (
            [
                [
                    {
                        "unique_id": "included-model",
                        "tags": ["tag1", "tag2"],
                    },
                ],
                ["tag1", "tag2", "tag3"],
                None,
                [
                    {
                        "unique_id": "included-model",
                        "tags": ["tag1", "tag2"],
                    },
                ],
            ]
        ),
    ],
)
def test_filter_nodes_by_tag(
    nodes: Iterable[dict],
    include_tags: list[str],
    exclude_tags: list[str],
    expected_return: Generator[dict, None, None],
):
    actual_return = filter_nodes_by_tag(iter(nodes), include_tags, exclude_tags)
    assert list(actual_return) == expected_return


@pytest.mark.parametrize(
    argnames=[
        "nodes",
        "include_packages",
        "exclude_packages",
        "expected_return",
    ],
    ids=[
        "One node in an included materialization",
        "One node in an included materialization, one out of scope",
        "Two nodes, both with different included materialization types",
        "One included, one excluded, one omitted",
        "No filter",
    ],
    argvalues=[
        (
            [
                [
                    {
                        "unique_id": "included-model",
                        "config": {"materialized": "table"},
                    },
                ],
                ["table"],
                None,
                [
                    {
                        "unique_id": "included-model",
                        "config": {"materialized": "table"},
                    },
                ],
            ]
        ),
        (
            [
                [
                    {
                        "unique_id": "included-model",
                        "config": {"materialized": "table"},
                    },
                    {
                        "unique_id": "excluded-model",
                        "config": {"materialized": "view"},
                    },
                ],
                ["table"],
                None,
                [
                    {
                        "unique_id": "included-model",
                        "config": {"materialized": "table"},
                    },
                ],
            ]
        ),
        (
            [
                [
                    {
                        "unique_id": "included-model",
                        "config": {"materialized": "table"},
                    },
                    {
                        "unique_id": "another-included-model",
                        "config": {"materialized": "view"},
                    },
                ],
                ["table", "view"],
                None,
                [
                    {
                        "unique_id": "included-model",
                        "config": {"materialized": "table"},
                    },
                    {
                        "unique_id": "another-included-model",
                        "config": {"materialized": "view"},
                    },
                ],
            ]
        ),
        (
            [
                [
                    {
                        "unique_id": "included-model",
                        "config": {"materialized": "table"},
                    },
                    {
                        "unique_id": "excluded-model",
                        "config": {"materialized": "view"},
                    },
                    {
                        "unique_id": "omitted-model",
                        "config": {"materialized": "ephemeral"},
                    },
                ],
                ["table"],
                ["view"],
                [
                    {
                        "unique_id": "included-model",
                        "config": {"materialized": "table"},
                    },
                ],
            ]
        ),
        (
            [
                [
                    {
                        "unique_id": "included-model",
                        "config": {"materialized": "table"},
                    },
                    {
                        "unique_id": "another-included-model",
                        "config": {"materialized": "view"},
                    },
                ],
                None,
                None,
                [
                    {
                        "unique_id": "included-model",
                        "config": {"materialized": "table"},
                    },
                    {
                        "unique_id": "another-included-model",
                        "config": {"materialized": "view"},
                    },
                ],
            ]
        ),
    ],
)
def test_filter_models_by_materialization_type(
    nodes: Iterable[dict],
    include_packages: list[str],
    exclude_packages: list[str],
    expected_return: Generator[dict, None, None],
):
    actual_return = filter_models_by_materialization_type(
        iter(nodes), include_packages, exclude_packages
    )
    assert list(actual_return) == expected_return


@pytest.mark.parametrize(
    argnames=[
        "nodes",
        "include_paths",
        "exclude_paths",
        "expected_return",
    ],
    ids=[
        "One node in an included path",
        "One node in an included path, one out of scope",
        "Two nodes, both with different included path",
        "One included, one excluded, one omitted",
        "No filter",
    ],
    argvalues=[
        (
            [
                [
                    {
                        "unique_id": "included-model",
                        "original_file_path": "test/model/path",
                    },
                ],
                [Path("test/model")],
                None,
                [
                    {
                        "unique_id": "included-model",
                        "original_file_path": "test/model/path",
                    },
                ],
            ]
        ),
        (
            [
                [
                    {
                        "unique_id": "included-model",
                        "original_file_path": "test/model/path",
                    },
                    {
                        "unique_id": "excluded-model",
                        "original_file_path": "test/another/path",
                    },
                ],
                [Path("test/model/path")],
                None,
                [
                    {
                        "unique_id": "included-model",
                        "original_file_path": "test/model/path",
                    },
                ],
            ]
        ),
        (
            [
                [
                    {
                        "unique_id": "included-model",
                        "original_file_path": "test/model/path",
                    },
                    {
                        "unique_id": "another-included-model",
                        "original_file_path": "test/another/path",
                    },
                ],
                [Path("test/model/path"), Path("test/another/path")],
                None,
                [
                    {
                        "unique_id": "included-model",
                        "original_file_path": "test/model/path",
                    },
                    {
                        "unique_id": "another-included-model",
                        "original_file_path": "test/another/path",
                    },
                ],
            ]
        ),
        (
            [
                [
                    {
                        "unique_id": "included-model",
                        "original_file_path": "test/model/path",
                    },
                    {
                        "unique_id": "excluded-model",
                        "original_file_path": "test/another/path",
                    },
                    {
                        "unique_id": "omitted-model",
                        "original_file_path": "test/one/more/path",
                    },
                ],
                [Path("test/model")],
                [Path("test/another")],
                [
                    {
                        "unique_id": "included-model",
                        "original_file_path": "test/model/path",
                    },
                ],
            ]
        ),
        (
            [
                [
                    {
                        "unique_id": "included-model",
                        "original_file_path": "test/model/path",
                    },
                    {
                        "unique_id": "another-included-model",
                        "original_file_path": "test/another/path",
                    },
                ],
                None,
                None,
                [
                    {
                        "unique_id": "included-model",
                        "original_file_path": "test/model/path",
                    },
                    {
                        "unique_id": "another-included-model",
                        "original_file_path": "test/another/path",
                    },
                ],
            ]
        ),
    ],
)
def test_filter_nodes_by_path(
    nodes: Iterable[dict],
    include_paths: list[Path],
    exclude_paths: list[Path],
    expected_return: Generator[dict, None, None],
):
    actual_return = filter_nodes_by_path(
        iter(nodes), include_paths=include_paths, exclude_paths=exclude_paths
    )
    assert list(actual_return) == expected_return


@pytest.mark.parametrize(
    argnames=[
        "nodes",
        "include_resource_types",
        "exclude_resource_types",
        "expected_return",
    ],
    ids=[
        "One node included",
        "One node included, one omitted",
        "Resource type not found in manifest",
        "Two nodes, both with different included resource types",
        "One included, one excluded, one omitted",
        "No filter",
    ],
    argvalues=[
        (
            [
                [
                    {
                        "unique_id": "included-model",
                        "resource_type": "model",
                    },
                ],
                ["model"],
                None,
                [
                    {
                        "unique_id": "included-model",
                        "resource_type": "model",
                    },
                ],
            ]
        ),
        (
            [
                [
                    {
                        "unique_id": "included-model",
                        "resource_type": "model",
                    },
                    {
                        "unique_id": "excluded-test",
                        "resource_type": "test",
                    },
                ],
                ["model"],
                None,
                [
                    {
                        "unique_id": "included-model",
                        "resource_type": "model",
                    },
                ],
            ]
        ),
        (
            [
                [
                    {
                        "unique_id": "excluded-model",
                        "resource_type": "model",
                    },
                ],
                ["test"],
                None,
                [],
            ]
        ),
        (
            [
                [
                    {
                        "unique_id": "included-model",
                        "resource_type": "model",
                    },
                    {
                        "unique_id": "included-test",
                        "resource_type": "test",
                    },
                ],
                ["model", "test"],
                None,
                [
                    {
                        "unique_id": "included-model",
                        "resource_type": "model",
                    },
                    {
                        "unique_id": "included-test",
                        "resource_type": "test",
                    },
                ],
            ]
        ),
        (
            [
                [
                    {
                        "unique_id": "included-model",
                        "resource_type": "model",
                    },
                    {
                        "unique_id": "excluded-test",
                        "resource_type": "test",
                    },
                    {
                        "unique_id": "omitted-model",
                        "resource_type": "seed",
                    },
                ],
                ["model"],
                ["test"],
                [
                    {
                        "unique_id": "included-model",
                        "resource_type": "model",
                    },
                ],
            ]
        ),
        (
            [
                [
                    {
                        "unique_id": "included-model",
                        "resource_type": "model",
                    },
                    {
                        "unique_id": "included-test",
                        "resource_type": "test",
                    },
                    {
                        "unique_id": "included-seed",
                        "resource_type": "seed",
                    },
                ],
                None,
                None,
                [
                    {
                        "unique_id": "included-model",
                        "resource_type": "model",
                    },
                    {
                        "unique_id": "included-test",
                        "resource_type": "test",
                    },
                    {
                        "unique_id": "included-seed",
                        "resource_type": "seed",
                    },
                ],
            ]
        ),
    ],
)
def test_filter_nodes_by_resource_type(
    nodes: Iterable[dict],
    include_resource_types: list[str],
    exclude_resource_types: list[str],
    expected_return: Generator[dict, None, None],
):
    actual_return = filter_nodes_by_resource_type(
        iter(nodes), include_resource_types, exclude_resource_types
    )
    assert list(actual_return) == expected_return


@pytest.mark.parametrize(
    ids=[
        "Two included macros",
        "One included, one excluded, one omitted",
        "No filter",
    ],
    argnames=["nodes", "filter_condition", "expected_macros"],
    argvalues=[
        (
            [
                [
                    {
                        "unique_id": "included-macro",
                        "package_name": "test_dbt_package",
                    },
                    {
                        "unique_id": "another-included-macro",
                        "package_name": "test_dbt_package",
                    },
                ],
                ManifestFilterConditions(include_packages=["test_dbt_package"]),
                [
                    {
                        "unique_id": "included-macro",
                        "package_name": "test_dbt_package",
                    },
                    {
                        "unique_id": "another-included-macro",
                        "package_name": "test_dbt_package",
                    },
                ],
            ]
        ),
        (
            [
                [
                    {
                        "unique_id": "included-macro",
                        "package_name": "test_dbt_package",
                    },
                    {
                        "unique_id": "excluded-macro",
                        "package_name": "another_dbt_package",
                    },
                    {
                        "unique_id": "omitted-macro",
                        "package_name": "one_more_dbt_package",
                    },
                ],
                ManifestFilterConditions(
                    include_packages=["test_dbt_package"],
                    exclude_packages=["another_dbt_package"],
                ),
                [
                    {
                        "unique_id": "included-macro",
                        "package_name": "test_dbt_package",
                    },
                ],
            ]
        ),
        (
            [
                [
                    {
                        "unique_id": "included-macro",
                        "package_name": "test_dbt_package",
                    },
                    {
                        "unique_id": "excluded-macro",
                        "package_name": "another_dbt_package",
                    },
                    {
                        "unique_id": "omitted-macro",
                        "package_name": "one_more_dbt_package",
                    },
                ],
                ManifestFilterConditions(),
                [
                    {
                        "unique_id": "included-macro",
                        "package_name": "test_dbt_package",
                    },
                    {
                        "unique_id": "excluded-macro",
                        "package_name": "another_dbt_package",
                    },
                    {
                        "unique_id": "omitted-macro",
                        "package_name": "one_more_dbt_package",
                    },
                ],
            ]
        ),
    ],
)
def test_get_macros_from_manifest(
    nodes: list[dict[str, str]],
    filter_condition: ManifestFilterConditions,
    expected_macros: list[dict[str, str]],
):
    with patch(
        "utils.artifact_data.get_json_artifact_data",
        return_value={
            "macros": {node["unique_id"]: node for node in nodes},
            "not_macros": "",
        },
    ) as mock_get_json_artifact_data:
        assert expected_macros == list(
            get_macros_from_manifest(Path(), filter_condition)
        )
        mock_get_json_artifact_data.assert_called_with(Path("manifest.json"))


@pytest.mark.parametrize(
    ids=[
        "Two included",
        "One included, one excluded, one omitted",
        "No filter",
        "One source with an included tag and an excluded tag",
    ],
    argnames=["nodes", "filter_condition", "expected_sources"],
    argvalues=[
        (
            [
                [
                    {
                        "unique_id": "included-source",
                        "package_name": "test_dbt_package",
                        "tags": ["test_tag"],
                        "original_file_path": "test/model/path",
                    },
                    {
                        "unique_id": "another-included-source",
                        "package_name": "test_dbt_package",
                        "tags": ["test_tag"],
                        "original_file_path": "test/another/path",
                    },
                ],
                ManifestFilterConditions(
                    include_packages=["test_dbt_package"],
                    include_tags=["test_tag"],
                    include_node_paths=[
                        Path("test/model/path"),
                        Path("test/another/path"),
                    ],
                ),
                [
                    {
                        "unique_id": "included-source",
                        "package_name": "test_dbt_package",
                        "tags": ["test_tag"],
                        "original_file_path": "test/model/path",
                    },
                    {
                        "unique_id": "another-included-source",
                        "package_name": "test_dbt_package",
                        "tags": ["test_tag"],
                        "original_file_path": "test/another/path",
                    },
                ],
            ]
        ),
        (
            [
                [
                    {
                        "unique_id": "included-source",
                        "package_name": "test_dbt_package",
                        "tags": ["test_tag"],
                        "original_file_path": "test/model/path",
                    },
                    {
                        "unique_id": "excluded-source",
                        "package_name": "another_dbt_package",
                        "tags": ["test_tag"],
                        "original_file_path": "test/another/path",
                    },
                    {
                        "unique_id": "omitted-source",
                        "package_name": "one_more_dbt_package",
                        "tags": ["test_tag"],
                        "original_file_path": "test/one/more/path",
                    },
                ],
                ManifestFilterConditions(
                    include_packages=["test_dbt_package"],
                    exclude_packages=["another_dbt_package"],
                ),
                [
                    {
                        "unique_id": "included-source",
                        "package_name": "test_dbt_package",
                        "tags": ["test_tag"],
                        "original_file_path": "test/model/path",
                    },
                ],
            ]
        ),
        (
            [
                [
                    {
                        "unique_id": "included-source",
                        "package_name": "test_dbt_package",
                        "tags": ["test_tag"],
                        "original_file_path": "test/model/path",
                    },
                    {
                        "unique_id": "another-included-source",
                        "package_name": "another_dbt_package",
                        "tags": ["test_tag"],
                        "original_file_path": "test/another/path",
                    },
                    {
                        "unique_id": "one-more-included-source",
                        "package_name": "one_more_dbt_package",
                        "tags": ["test_tag"],
                        "original_file_path": "test/one/more/path",
                    },
                ],
                ManifestFilterConditions(),
                [
                    {
                        "unique_id": "included-source",
                        "package_name": "test_dbt_package",
                        "tags": ["test_tag"],
                        "original_file_path": "test/model/path",
                    },
                    {
                        "unique_id": "another-included-source",
                        "package_name": "another_dbt_package",
                        "tags": ["test_tag"],
                        "original_file_path": "test/another/path",
                    },
                    {
                        "unique_id": "one-more-included-source",
                        "package_name": "one_more_dbt_package",
                        "tags": ["test_tag"],
                        "original_file_path": "test/one/more/path",
                    },
                ],
            ]
        ),
        (
            [
                [
                    {
                        "unique_id": "excluded-source",
                        "package_name": "test_dbt_package",
                        "tags": ["included_tag", "excluded_tag"],
                        "original_file_path": "test/model/path",
                    },
                ],
                ManifestFilterConditions(
                    include_tags=["included_tag"], exclude_tags=["excluded_tag"]
                ),
                [],
            ]
        ),
    ],
)
def test_get_sources_from_manifest(
    nodes: list[dict[str, str]],
    filter_condition: ManifestFilterConditions,
    expected_sources: list[dict[str, str]],
):
    with patch(
        "utils.artifact_data.get_json_artifact_data",
        return_value={
            "sources": {node["unique_id"]: node for node in nodes},
            "not_sources": "",
        },
    ) as mock_get_json_artifact_data:
        assert expected_sources == list(
            get_sources_from_manifest(Path(), filter_condition)
        )
        mock_get_json_artifact_data.assert_called_with(Path("manifest.json"))


@pytest.mark.parametrize(
    ids=[
        "Two included",
        "One included, one excluded, one omitted",
        "No filter",
        "One source with an included tag and an excluded tag",
    ],
    argnames=["nodes", "filter_condition", "expected_nodes"],
    argvalues=[
        (
            [
                [
                    {
                        "unique_id": "included-model",
                        "package_name": "test_dbt_package",
                        "tags": ["test_tag"],
                        "original_file_path": "test/model/path",
                    },
                    {
                        "unique_id": "included-test",
                        "package_name": "test_dbt_package",
                        "tags": ["test_tag"],
                        "original_file_path": "test/another/path",
                    },
                ],
                ManifestFilterConditions(
                    include_packages=["test_dbt_package"],
                    include_tags=["test_tag"],
                    include_node_paths=[
                        Path("test/model/path"),
                        Path("test/another/path"),
                    ],
                ),
                [
                    {
                        "unique_id": "included-model",
                        "package_name": "test_dbt_package",
                        "tags": ["test_tag"],
                        "original_file_path": "test/model/path",
                    },
                    {
                        "unique_id": "included-test",
                        "package_name": "test_dbt_package",
                        "tags": ["test_tag"],
                        "original_file_path": "test/another/path",
                    },
                ],
            ]
        ),
        (
            [
                [
                    {
                        "unique_id": "included-model",
                        "package_name": "test_dbt_package",
                        "tags": ["test_tag"],
                        "original_file_path": "test/model/path",
                    },
                    {
                        "unique_id": "excluded-test",
                        "package_name": "another_dbt_package",
                        "tags": ["test_tag"],
                        "original_file_path": "test/another/path",
                    },
                    {
                        "unique_id": "omitted-seed",
                        "package_name": "one_more_dbt_package",
                        "tags": ["test_tag"],
                        "original_file_path": "test/one/more/path",
                    },
                ],
                ManifestFilterConditions(
                    include_packages=["test_dbt_package"],
                    exclude_packages=["another_dbt_package"],
                ),
                [
                    {
                        "unique_id": "included-model",
                        "package_name": "test_dbt_package",
                        "tags": ["test_tag"],
                        "original_file_path": "test/model/path",
                    },
                ],
            ]
        ),
        (
            [
                [
                    {
                        "unique_id": "included-model",
                        "package_name": "test_dbt_package",
                        "tags": ["test_tag"],
                        "original_file_path": "test/model/path",
                    },
                    {
                        "unique_id": "included-test",
                        "package_name": "another_dbt_package",
                        "tags": ["test_tag"],
                        "original_file_path": "test/another/path",
                    },
                    {
                        "unique_id": "included-seed",
                        "package_name": "one_more_dbt_package",
                        "tags": ["test_tag"],
                        "original_file_path": "test/one/more/path",
                    },
                ],
                ManifestFilterConditions(),
                [
                    {
                        "unique_id": "included-model",
                        "package_name": "test_dbt_package",
                        "tags": ["test_tag"],
                        "original_file_path": "test/model/path",
                    },
                    {
                        "unique_id": "included-test",
                        "package_name": "another_dbt_package",
                        "tags": ["test_tag"],
                        "original_file_path": "test/another/path",
                    },
                    {
                        "unique_id": "included-seed",
                        "package_name": "one_more_dbt_package",
                        "tags": ["test_tag"],
                        "original_file_path": "test/one/more/path",
                    },
                ],
            ]
        ),
        (
            [
                [
                    {
                        "unique_id": "excluded-model",
                        "package_name": "test_dbt_package",
                        "tags": ["included_tag", "excluded_tag"],
                        "original_file_path": "test/model/path",
                    },
                ],
                ManifestFilterConditions(
                    include_tags=["included_tag"], exclude_tags=["excluded_tag"]
                ),
                [],
            ]
        ),
    ],
)
def test_get_nodes_from_manifest(
    nodes: list[dict[str, str]],
    filter_condition: ManifestFilterConditions,
    expected_nodes: list[dict[str, str]],
):
    with patch(
        "utils.artifact_data.get_json_artifact_data",
        return_value={
            "nodes": {node["unique_id"]: node for node in nodes},
            "not_nodes": "",
        },
    ) as mock_get_json_artifact_data:
        assert expected_nodes == list(get_nodes_from_manifest(Path(), filter_condition))
        mock_get_json_artifact_data.assert_called_with(Path("manifest.json"))


@pytest.mark.parametrize(
    ids=[
        "Two included",
        "One included, one excluded, one omitted",
        "No filter",
        "One source with an included tag and an excluded tag",
    ],
    argnames=["nodes", "filter_condition", "expected_nodes"],
    argvalues=[
        (
            [
                [
                    {
                        "unique_id": "included-model",
                        "package_name": "test_dbt_package",
                        "tags": ["test_tag"],
                        "resource_type": "model",
                    },
                    {
                        "unique_id": "another-included-model",
                        "package_name": "test_dbt_package",
                        "tags": ["test_tag"],
                        "resource_type": "model",
                    },
                ],
                ManifestFilterConditions(
                    include_packages=["test_dbt_package"], include_tags=["test_tag"]
                ),
                [
                    {
                        "unique_id": "included-model",
                        "package_name": "test_dbt_package",
                        "tags": ["test_tag"],
                        "resource_type": "model",
                    },
                    {
                        "unique_id": "another-included-model",
                        "package_name": "test_dbt_package",
                        "tags": ["test_tag"],
                        "resource_type": "model",
                    },
                ],
            ]
        ),
        (
            [
                [
                    {
                        "unique_id": "included-model",
                        "package_name": "test_dbt_package",
                        "tags": ["test_tag"],
                        "resource_type": "model",
                    },
                    {
                        "unique_id": "excluded-model",
                        "package_name": "another_dbt_package",
                        "tags": ["test_tag"],
                        "resource_type": "model",
                    },
                    {
                        "unique_id": "omitted-model",
                        "package_name": "one_more_dbt_package",
                        "tags": ["test_tag"],
                        "resource_type": "model",
                    },
                ],
                ManifestFilterConditions(
                    include_packages=["test_dbt_package"],
                    exclude_packages=["another_dbt_package"],
                ),
                [
                    {
                        "unique_id": "included-model",
                        "package_name": "test_dbt_package",
                        "tags": ["test_tag"],
                        "resource_type": "model",
                    },
                ],
            ]
        ),
        (
            [
                [
                    {
                        "unique_id": "included-model",
                        "package_name": "test_dbt_package",
                        "tags": ["test_tag"],
                        "resource_type": "model",
                    },
                    {
                        "unique_id": "another-included-model",
                        "package_name": "another_dbt_package",
                        "tags": ["test_tag"],
                        "resource_type": "model",
                    },
                    {
                        "unique_id": "one-more-included-model",
                        "package_name": "one_more_dbt_package",
                        "tags": ["test_tag"],
                        "resource_type": "model",
                    },
                ],
                ManifestFilterConditions(),
                [
                    {
                        "unique_id": "included-model",
                        "package_name": "test_dbt_package",
                        "tags": ["test_tag"],
                        "resource_type": "model",
                    },
                    {
                        "unique_id": "another-included-model",
                        "package_name": "another_dbt_package",
                        "tags": ["test_tag"],
                        "resource_type": "model",
                    },
                    {
                        "unique_id": "one-more-included-model",
                        "package_name": "one_more_dbt_package",
                        "tags": ["test_tag"],
                        "resource_type": "model",
                    },
                ],
            ]
        ),
        (
            [
                [
                    {
                        "unique_id": "excluded-model",
                        "package_name": "test_dbt_package",
                        "tags": ["included_tag", "excluded_tag"],
                        "resource_type": "model",
                    },
                ],
                ManifestFilterConditions(
                    include_tags=["included_tag"], exclude_tags=["excluded_tag"]
                ),
                [],
            ]
        ),
    ],
)
def test_get_models_from_manifest(
    nodes: list[dict[str, str]],
    filter_condition: ManifestFilterConditions,
    expected_nodes: list[dict[str, str]],
):
    with patch(
        "utils.artifact_data.get_json_artifact_data",
        return_value={
            "nodes": {node["unique_id"]: node for node in nodes},
            "not_nodes": "",
        },
    ) as mock_get_json_artifact_data:
        assert expected_nodes == list(
            get_models_from_manifest(
                manifest_dir=Path(), filter_conditions=filter_condition
            )
        )
        mock_get_json_artifact_data.assert_called_with(Path("manifest.json"))


@pytest.mark.parametrize(
    ids=["base case", "Empty/None"],
    argnames=["kwargs", "expected_attributes"],
    argvalues=[
        (
            {
                "include_materializations": ("table", "view"),
                "include_packages": ["test_dbt_project", "another_dbt_project"],
                "include_tags": {"test_tag", "another_tag"},
                "include_node_paths": {
                    Path("test/model/path"),
                    Path("test/another/path"),
                },
                "exclude_materializations": ("ephemeral", "incremental"),
                "exclude_packages": ["one_more_dbt_project"],
                "exclude_tags": {"one_more_tag"},
                "exclude_node_paths": {Path("test/one/more/path")},
            },
            {
                "include_materializations": {"table", "view"},
                "include_packages": {"test_dbt_project", "another_dbt_project"},
                "include_tags": {"test_tag", "another_tag"},
                "include_node_paths": {
                    Path("test/model/path"),
                    Path("test/another/path"),
                },
                "exclude_materializations": {"ephemeral", "incremental"},
                "exclude_packages": {"one_more_dbt_project"},
                "exclude_tags": {"one_more_tag"},
                "exclude_node_paths": {Path("test/one/more/path")},
            },
        ),
        (
            {
                "include_materializations": (),
                "include_packages": None,
                "include_tags": None,
                "include_node_paths": None,
                "exclude_materializations": [],
                "exclude_packages": set(),
                "exclude_tags": None,
                "exclude_node_paths": None,
            },
            {
                "include_materializations": None,
                "include_packages": None,
                "include_tags": None,
                "include_node_paths": None,
                "exclude_materializations": None,
                "exclude_packages": None,
                "exclude_tags": None,
                "exclude_node_paths": None,
            },
        ),
    ],
)
def test_manifest_filter_conditions_init(kwargs, expected_attributes):
    for attribute_name, attribute_value in expected_attributes.items():
        assert (
            getattr(ManifestFilterConditions(**kwargs), attribute_name)
            == attribute_value
        )


@pytest.mark.parametrize(
    ids=["base case", "Empty/None"],
    argnames=["kwargs", "expected_summary"],
    argvalues=[
        (
            {
                "include_materializations": ("table", "view"),
                "include_packages": ["test_dbt_project", "another_dbt_project"],
                "include_tags": {"test_tag", "another_tag"},
                "include_node_paths": {
                    Path("test/model/path"),
                    Path("test/another/path"),
                },
                "exclude_materializations": ("ephemeral", "incremental"),
                "exclude_packages": ["one_more_dbt_project"],
                "exclude_tags": {"one_more_tag"},
                "exclude_node_paths": {Path("test/one/more/path")},
            },
            colour_message(
                """Including:
	materialized: table, view
	tags: another_tag, test_tag
	packages: another_dbt_project, test_dbt_project
	node paths: test/another/path, test/model/path
Excluding:
	materialized: ephemeral, incremental
	tags: one_more_tag
	packages: one_more_dbt_project
	node paths: test/one/more/path""",
                emphasis=ConsoleEmphasis.ITALIC,
            ),
        ),
        (
            {
                "include_materializations": (),
                "include_packages": None,
                "include_tags": None,
                "include_node_paths": None,
                "exclude_materializations": [],
                "exclude_packages": set(),
                "exclude_tags": None,
                "exclude_node_paths": None,
            },
            colour_message("", emphasis=ConsoleEmphasis.ITALIC),
        ),
    ],
)
def test_manifest_filter_conditions_summary(kwargs, expected_summary):
    assert ManifestFilterConditions(**kwargs).summary == expected_summary


@pytest.mark.parametrize(
    ids=["same", "different"],
    argnames=["instance_1", "instance_2", "expected_return"],
    argvalues=[
        (
            ManifestFilterConditions(
                include_materializations=("table", "view"),
                include_packages=("test_dbt_project", "another_dbt_project"),
                include_tags=("test_tag", "another_tag"),
                include_node_paths=(Path("test/model/path"), Path("test/another/path")),
                exclude_materializations=("ephemeral", "incremental"),
                exclude_packages=("one_more_dbt_project",),
                exclude_tags=("one_more_tag",),
                exclude_node_paths=(Path("test/one/more/path"),),
            ),
            ManifestFilterConditions(
                include_materializations=("table", "view"),
                include_packages=("test_dbt_project", "another_dbt_project"),
                include_tags=("test_tag", "another_tag"),
                include_node_paths=(Path("test/model/path"), Path("test/another/path")),
                exclude_materializations=("ephemeral", "incremental"),
                exclude_packages=("one_more_dbt_project",),
                exclude_tags=("one_more_tag",),
                exclude_node_paths=(Path("test/one/more/path"),),
            ),
            True,
        ),
        (
            ManifestFilterConditions(
                include_materializations=("table", "view"),
                include_packages=("test_dbt_project", "another_dbt_project"),
                include_tags=("test_tag", "another_tag"),
                include_node_paths=(Path("test/model/path"), Path("test/another/path")),
                exclude_materializations=("ephemeral", "incremental"),
                exclude_packages=("one_more_dbt_project",),
                exclude_tags=("one_more_tag",),
                exclude_node_paths=(Path("test/one/more/path"),),
            ),
            ManifestFilterConditions(
                include_materializations=("table", "view"),
            ),
            False,
        ),
    ],
)
def test_manifest_filter_conditions_eq(
    instance_1: ManifestFilterConditions,
    instance_2: ManifestFilterConditions,
    expected_return: bool,
):
    assert (instance_1 == instance_2) is expected_return
