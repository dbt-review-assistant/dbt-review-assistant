import json
from pathlib import Path
from contextlib import nullcontext as does_not_raise
from typing import Iterable, Generator, Any
from unittest.mock import patch, Mock

from utils.artifact_data import (
    get_json_artifact_data,
    Manifest,
    Catalog,
    MANIFEST_FILE_NAME,
    CATALOG_FILE_NAME,
)
from utils.catalog_object.catalog_table import CatalogTable
from utils.manifest_filter_conditions import ManifestFilterConditions
from utils.console_formatting import colour_message, ConsoleEmphasis
import pytest

from utils.manifest_object.macro import Macro
from utils.manifest_object.node.analysis import ManifestAnalysis
from utils.manifest_object.node.function import ManifestFunction
from utils.manifest_object.node.generic_test import GenericTest
from utils.manifest_object.node.model.model import ManifestModel
from utils.manifest_object.node.seed import ManifestSeed
from utils.manifest_object.node.singular_test import SingularTest
from utils.manifest_object.node.snapshot import ManifestSnapshot
from utils.manifest_object.source.source import ManifestSource
from utils.manifest_object.unit_test import UnitTest


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


@patch("utils.artifact_data.get_json_artifact_data")
def test_manifest_init(mock_get_json_artifact_data):
    mock_data = Mock()
    mock_get_json_artifact_data.return_value = mock_data
    path = Path("test")
    filters = ManifestFilterConditions()
    instance = Manifest(manifest_dir=path, filter_conditions=filters)
    mock_get_json_artifact_data.assert_called_with(path / MANIFEST_FILE_NAME)
    assert instance.filter_conditions is filters
    assert instance.data is mock_data


@patch("utils.artifact_data.get_json_artifact_data")
def test_manifest_nodes(mock_get_json_artifact_data):
    nodes = Mock()
    mock_data = {"nodes": nodes, "sources": {}, "unit_tests": {}}
    mock_get_json_artifact_data.return_value = mock_data
    path = Path("test")
    filters = ManifestFilterConditions()
    instance = Manifest(manifest_dir=path, filter_conditions=filters)
    assert instance.nodes is nodes


@patch("utils.artifact_data.get_json_artifact_data")
def test_manifest_models(mock_get_json_artifact_data):
    filters = ManifestFilterConditions()
    mock_data = {
        "nodes": {
            "test_model": {"resource_type": "model"},
            "another_model": {"resource_type": "model"},
            "test_seed": {"resource_type": "seed"},
        },
        "sources": {},
        "unit_tests": {},
    }
    expected_models = {
        "test_model": ManifestModel(
            data={"resource_type": "model"},
            filter_conditions=filters,
        ),
        "another_model": ManifestModel(
            data={"resource_type": "model"},
            filter_conditions=filters,
        ),
    }
    mock_get_json_artifact_data.return_value = mock_data
    path = Path("test")
    instance = Manifest(manifest_dir=path, filter_conditions=filters)
    assert instance.models == expected_models


@patch("utils.artifact_data.get_json_artifact_data")
def test_manifest_in_scope_models(mock_get_json_artifact_data):
    filters = ManifestFilterConditions(include_packages=["test_package"])
    mock_data = {
        "nodes": {
            "test_model": {"resource_type": "model", "package_name": "test_package"},
            "another_model": {"resource_type": "model", "package_name": "test_package"},
            "one_more_model": {
                "resource_type": "model",
                "package_name": "another_package",
            },
            "test_seed": {"resource_type": "seed"},
        },
        "sources": {},
        "unit_tests": {},
    }
    expected_models = [
        ManifestModel(
            data={"resource_type": "model", "package_name": "test_package"},
            filter_conditions=filters,
        ),
        ManifestModel(
            data={"resource_type": "model", "package_name": "test_package"},
            filter_conditions=filters,
        ),
    ]
    mock_get_json_artifact_data.return_value = mock_data
    path = Path("test")
    instance = Manifest(manifest_dir=path, filter_conditions=filters)
    assert list(instance.in_scope_models) == expected_models


@pytest.mark.parametrize(
    argnames=["model_id", "expected_return"],
    ids=["model found", "model not found"],
    argvalues=[
        (
            "test_model",
            ManifestModel(
                data={"resource_type": "model", "package_name": "test_package"},
                filter_conditions=ManifestFilterConditions(),
            ),
        ),
        ("no_such_model", None),
    ],
)
@patch("utils.artifact_data.get_json_artifact_data")
def test_manifest_get_model(mock_get_json_artifact_data, model_id, expected_return):
    filters = ManifestFilterConditions()
    mock_data = {
        "nodes": {
            "test_model": {"resource_type": "model", "package_name": "test_package"},
            "another_model": {"resource_type": "model", "package_name": "test_package"},
            "one_more_model": {
                "resource_type": "model",
                "package_name": "another_package",
            },
            "test_seed": {"resource_type": "seed"},
        },
        "sources": {},
        "unit_tests": {},
    }
    mock_get_json_artifact_data.return_value = mock_data
    path = Path("test")
    instance = Manifest(manifest_dir=path, filter_conditions=filters)
    result = instance.get_model(model_id)
    if expected_return:
        assert result == expected_return
    else:
        assert result is None


@patch("utils.artifact_data.get_json_artifact_data")
def test_manifest_generic_tests(mock_get_json_artifact_data):
    filters = ManifestFilterConditions()
    mock_data = {
        "nodes": {
            "test_test": {"resource_type": "test"},
            "another_test": {"resource_type": "test"},
            "test_seed": {"resource_type": "seed"},
        },
        "sources": {},
        "unit_tests": {},
    }
    expected_tests = {
        "test_test": GenericTest(
            data={"resource_type": "test"},
            filter_conditions=filters,
        ),
        "another_test": GenericTest(
            data={"resource_type": "test"},
            filter_conditions=filters,
        ),
    }
    mock_get_json_artifact_data.return_value = mock_data
    path = Path("test")
    instance = Manifest(manifest_dir=path, filter_conditions=filters)
    assert instance.generic_tests == expected_tests


@patch("utils.artifact_data.get_json_artifact_data")
def test_manifest_snapshots(mock_get_json_artifact_data):
    filters = ManifestFilterConditions()
    mock_data = {
        "nodes": {
            "test_snapshot": {"resource_type": "snapshot"},
            "another_snapshot": {"resource_type": "snapshot"},
            "test_seed": {"resource_type": "seed"},
        },
        "sources": {},
        "unit_tests": {},
    }
    expected_snapshots = {
        "test_snapshot": ManifestSnapshot(
            data={"resource_type": "snapshot"},
            filter_conditions=filters,
        ),
        "another_snapshot": ManifestSnapshot(
            data={"resource_type": "snapshot"},
            filter_conditions=filters,
        ),
    }
    mock_get_json_artifact_data.return_value = mock_data
    path = Path("test")
    instance = Manifest(manifest_dir=path, filter_conditions=filters)
    assert instance.snapshots == expected_snapshots


@patch("utils.artifact_data.get_json_artifact_data")
def test_manifest_seeds(mock_get_json_artifact_data):
    filters = ManifestFilterConditions()
    mock_data = {
        "nodes": {
            "test_seed": {"resource_type": "seed"},
            "another_seed": {"resource_type": "seed"},
            "test_model": {"resource_type": "model"},
        },
        "sources": {},
        "unit_tests": {},
    }
    expected_seeds = {
        "test_seed": ManifestSeed(
            data={"resource_type": "seed"},
            filter_conditions=filters,
        ),
        "another_seed": ManifestSeed(
            data={"resource_type": "seed"},
            filter_conditions=filters,
        ),
    }
    mock_get_json_artifact_data.return_value = mock_data
    path = Path("test")
    instance = Manifest(manifest_dir=path, filter_conditions=filters)
    assert instance.seeds == expected_seeds


@patch("utils.artifact_data.get_json_artifact_data")
def test_manifest_analyses(mock_get_json_artifact_data):
    filters = ManifestFilterConditions()
    mock_data = {
        "nodes": {
            "test_analysis": {"resource_type": "analysis"},
            "another_analysis": {"resource_type": "analysis"},
            "test_seed": {"resource_type": "seed"},
        },
        "sources": {},
        "unit_tests": {},
    }
    expected_analyses = {
        "test_analysis": ManifestAnalysis(
            data={"resource_type": "analysis"},
            filter_conditions=filters,
        ),
        "another_analysis": ManifestAnalysis(
            data={"resource_type": "analysis"},
            filter_conditions=filters,
        ),
    }
    mock_get_json_artifact_data.return_value = mock_data
    path = Path("test")
    instance = Manifest(manifest_dir=path, filter_conditions=filters)
    assert instance.analyses == expected_analyses


@patch("utils.artifact_data.get_json_artifact_data")
def test_manifest_singular_tests(mock_get_json_artifact_data):
    filters = ManifestFilterConditions()
    mock_data = {
        "nodes": {
            "test_singular_test": {"resource_type": "singular_test"},
            "another_singular_test": {"resource_type": "singular_test"},
            "test_seed": {"resource_type": "seed"},
        },
        "sources": {},
        "unit_tests": {},
    }
    expected_singular_tests = {
        "test_singular_test": SingularTest(
            data={"resource_type": "singular_test"},
            filter_conditions=filters,
        ),
        "another_singular_test": SingularTest(
            data={"resource_type": "singular_test"},
            filter_conditions=filters,
        ),
    }
    mock_get_json_artifact_data.return_value = mock_data
    path = Path("test")
    instance = Manifest(manifest_dir=path, filter_conditions=filters)
    assert instance.singular_tests == expected_singular_tests


@patch("utils.artifact_data.get_json_artifact_data")
def test_manifest_functions(mock_get_json_artifact_data):
    filters = ManifestFilterConditions()
    mock_data = {
        "nodes": {
            "test_function": {"resource_type": "function"},
            "another_function": {"resource_type": "function"},
            "test_seed": {"resource_type": "seed"},
        },
        "sources": {},
        "unit_tests": {},
    }
    expected_functions = {
        "test_function": ManifestFunction(
            data={"resource_type": "function"},
            filter_conditions=filters,
        ),
        "another_function": ManifestFunction(
            data={"resource_type": "function"},
            filter_conditions=filters,
        ),
    }
    mock_get_json_artifact_data.return_value = mock_data
    path = Path("test")
    instance = Manifest(manifest_dir=path, filter_conditions=filters)
    assert instance.functions == expected_functions


@patch("utils.artifact_data.get_json_artifact_data")
def test_manifest_sources(mock_get_json_artifact_data):
    filters = ManifestFilterConditions()
    mock_data = {
        "sources": {
            "test_source": {"resource_type": "source"},
            "another_source": {"resource_type": "source"},
        },
        "unit_tests": {},
    }
    expected_sources = {
        "test_source": ManifestSource(
            data={"resource_type": "source"},
            filter_conditions=filters,
        ),
        "another_source": ManifestSource(
            data={"resource_type": "source"},
            filter_conditions=filters,
        ),
    }
    mock_get_json_artifact_data.return_value = mock_data
    path = Path("test")
    instance = Manifest(manifest_dir=path, filter_conditions=filters)
    assert instance.sources == expected_sources


@patch("utils.artifact_data.get_json_artifact_data")
def test_manifest_in_scope_sources(mock_get_json_artifact_data):
    filters = ManifestFilterConditions(include_packages=["test_package"])
    mock_data = {
        "sources": {
            "test_source": {"resource_type": "source", "package_name": "test_package"},
            "another_source": {
                "resource_type": "source",
                "package_name": "test_package",
            },
            "one_more_source": {
                "resource_type": "source",
                "package_name": "another_package",
            },
        },
        "unit_tests": {},
    }
    expected_sources = [
        ManifestSource(
            data={"resource_type": "source", "package_name": "test_package"},
            filter_conditions=filters,
        ),
        ManifestSource(
            data={"resource_type": "source", "package_name": "test_package"},
            filter_conditions=filters,
        ),
    ]
    mock_get_json_artifact_data.return_value = mock_data
    path = Path("test")
    instance = Manifest(manifest_dir=path, filter_conditions=filters)
    assert list(instance.in_scope_sources) == expected_sources


@patch("utils.artifact_data.get_json_artifact_data")
def test_manifest_macros(mock_get_json_artifact_data):
    filters = ManifestFilterConditions()
    mock_data = {
        "macros": {
            "test_macro": {"resource_type": "macro"},
            "another_macro": {"resource_type": "macro"},
        },
        "unit_tests": {},
    }
    expected_macros = {
        "test_macro": Macro(
            data={"resource_type": "macro"},
            filter_conditions=filters,
        ),
        "another_macro": Macro(
            data={"resource_type": "macro"},
            filter_conditions=filters,
        ),
    }
    mock_get_json_artifact_data.return_value = mock_data
    path = Path("test")
    instance = Manifest(manifest_dir=path, filter_conditions=filters)
    assert instance.macros == expected_macros


@patch("utils.artifact_data.get_json_artifact_data")
def test_manifest_in_scope_macros(mock_get_json_artifact_data):
    filters = ManifestFilterConditions(include_packages=["test_package"])
    mock_data = {
        "macros": {
            "test_macro": {"resource_type": "macro", "package_name": "test_package"},
            "another_source": {
                "resource_type": "macro",
                "package_name": "test_package",
            },
            "one_more_source": {
                "resource_type": "macro",
                "package_name": "another_package",
            },
        },
        "unit_tests": {},
    }
    expected_sources = [
        Macro(
            data={"resource_type": "macro", "package_name": "test_package"},
            filter_conditions=filters,
        ),
        Macro(
            data={"resource_type": "macro", "package_name": "test_package"},
            filter_conditions=filters,
        ),
    ]
    mock_get_json_artifact_data.return_value = mock_data
    path = Path("test")
    instance = Manifest(manifest_dir=path, filter_conditions=filters)
    assert list(instance.in_scope_macros) == expected_sources


@patch("utils.artifact_data.get_json_artifact_data")
def test_manifest_unit_tests(mock_get_json_artifact_data):
    filters = ManifestFilterConditions()
    mock_data = {
        "unit_tests": {
            "test_unit_test": {"resource_type": "unit_test"},
            "another_unit_test": {"resource_type": "unit_test"},
        },
        "seeds": {},
    }
    expected_unit_tests = {
        "test_unit_test": UnitTest(
            data={"resource_type": "unit_test"},
            filter_conditions=filters,
        ),
        "another_unit_test": UnitTest(
            data={"resource_type": "unit_test"},
            filter_conditions=filters,
        ),
    }
    mock_get_json_artifact_data.return_value = mock_data
    path = Path("test")
    instance = Manifest(manifest_dir=path, filter_conditions=filters)
    assert instance.unit_tests == expected_unit_tests


@patch("utils.artifact_data.get_json_artifact_data")
def test_manifest_child_maps(mock_get_json_artifact_data):
    filters = ManifestFilterConditions()
    mock_child_map = Mock()
    mock_data = {
        "child_map": mock_child_map,
        "seeds": {},
    }
    mock_get_json_artifact_data.return_value = mock_data
    path = Path("test")
    instance = Manifest(manifest_dir=path, filter_conditions=filters)
    assert instance.child_map is mock_child_map


@patch("utils.artifact_data.get_json_artifact_data")
def test_catalog_init(mock_get_json_artifact_data):
    mock_data = Mock()
    mock_get_json_artifact_data.return_value = mock_data
    path = Path("test")
    instance = Catalog(catalog_dir=path)
    mock_get_json_artifact_data.assert_called_with(path / CATALOG_FILE_NAME)
    assert instance.data is mock_data


@patch("utils.artifact_data.get_json_artifact_data")
def test_catalog_nodes(mock_get_json_artifact_data):
    mock_data = {
        "nodes": {
            "test_table": {"name": "test_table"},
            "another_table": {"name": "another_table"},
        },
        "sources": {},
        "unit_tests": {},
    }
    mock_get_json_artifact_data.return_value = mock_data
    path = Path("test")
    expected_nodes = {
        "test_table": CatalogTable({"name": "test_table"}),
        "another_table": CatalogTable({"name": "another_table"}),
    }
    instance = Catalog(catalog_dir=path)
    assert instance.nodes == expected_nodes


@patch("utils.artifact_data.get_json_artifact_data")
def test_catalog_sources(mock_get_json_artifact_data):
    mock_data = {
        "sources": {
            "test_source": {"resource_type": "source"},
            "another_source": {"resource_type": "source"},
        },
        "unit_tests": {},
    }
    expected_sources = {
        "test_source": CatalogTable(data={"resource_type": "source"}),
        "another_source": CatalogTable(
            data={"resource_type": "source"},
        ),
    }
    mock_get_json_artifact_data.return_value = mock_data
    path = Path("test")
    instance = Catalog(catalog_dir=path)
    assert instance.sources == expected_sources


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
#         "One node included",
#         "One node included, one omitted",
#         "Package not found in manifest",
#         "Two nodes, both with different included packages",
#         "One included, one excluded, one omitted",
#         "No filter",
#     ],
#     argvalues=[
#         (
#             [
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "package_name": "test_dbt_package",
#                     },
#                 ],
#                 ["test_dbt_package"],
#                 None,
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "package_name": "test_dbt_package",
#                     },
#                 ],
#             ]
#         ),
#         (
#             [
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "package_name": "test_dbt_package",
#                     },
#                     {
#                         "unique_id": "excluded-model",
#                         "package_name": "another_dbt_package",
#                     },
#                 ],
#                 ["test_dbt_package"],
#                 None,
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "package_name": "test_dbt_package",
#                     },
#                 ],
#             ]
#         ),
#         (
#             [
#                 [
#                     {
#                         "unique_id": "excluded-model",
#                         "package_name": "test_dbt_package",
#                         "description": None,
#                     },
#                 ],
#                 ["another_dbt_package"],
#                 None,
#                 [],
#             ]
#         ),
#         (
#             [
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "package_name": "test_dbt_package",
#                     },
#                     {
#                         "unique_id": "another-included-model",
#                         "package_name": "another_dbt_package",
#                     },
#                 ],
#                 ["test_dbt_package", "another_dbt_package"],
#                 None,
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "package_name": "test_dbt_package",
#                     },
#                     {
#                         "unique_id": "another-included-model",
#                         "package_name": "another_dbt_package",
#                     },
#                 ],
#             ]
#         ),
#         (
#             [
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "package_name": "test_dbt_package",
#                     },
#                     {
#                         "unique_id": "excluded-model",
#                         "package_name": "another_dbt_package",
#                     },
#                     {
#                         "unique_id": "omitted-model",
#                         "package_name": "one_more_dbt_package",
#                     },
#                 ],
#                 ["test_dbt_package"],
#                 ["another_dbt_package"],
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "package_name": "test_dbt_package",
#                     },
#                 ],
#             ]
#         ),
#         (
#             [
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "package_name": "test_dbt_package",
#                     },
#                     {
#                         "unique_id": "another-included-model",
#                         "package_name": "another_dbt_package",
#                     },
#                     {
#                         "unique_id": "one-more-model",
#                         "package_name": "one_more_dbt_package",
#                     },
#                 ],
#                 None,
#                 None,
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "package_name": "test_dbt_package",
#                     },
#                     {
#                         "unique_id": "another-included-model",
#                         "package_name": "another_dbt_package",
#                     },
#                     {
#                         "unique_id": "one-more-model",
#                         "package_name": "one_more_dbt_package",
#                     },
#                 ],
#             ]
#         ),
#     ],
# )
# def test_filter_nodes_by_package(
#     nodes: Iterable[dict],
#     include_packages: list[str],
#     exclude_packages: list[str],
#     expected_return: Generator[dict, None, None],
# ):
#     actual_return = filter_nodes_by_package(
#         iter(nodes), include_packages, exclude_packages
#     )
#     assert list(actual_return) == expected_return
#
#
# @pytest.mark.parametrize(
#     argnames=[
#         "nodes",
#         "include_tags",
#         "exclude_tags",
#         "expected_return",
#     ],
#     ids=[
#         "One node with an included tag",
#         "One node with an included tag, and one node with an excluded tag",
#         "One node with an included tag and an excluded tag",
#         "Two nodes, both with different included tags",
#         "One node with an included tag and an excluded tag",
#         "No filters",
#         "One node included, tags under config key",
#         "One node having all included tags",
#         "One node having all but one included tags",
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
#         (
#             [
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "tags": ["test_tag"],
#                     },
#                     {
#                         "unique_id": "excluded-model",
#                         "tags": ["another_tag"],
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
#         (
#             [
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "tags": ["test_tag", "another_tag"],
#                     },
#                 ],
#                 ["test_tag"],
#                 None,
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "tags": ["test_tag", "another_tag"],
#                     },
#                 ],
#             ]
#         ),
#         (
#             [
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "tags": ["test_tag"],
#                     },
#                     {
#                         "unique_id": "another-included-model",
#                         "tags": ["another_tag"],
#                     },
#                 ],
#                 ["test_tag", "another_tag"],
#                 None,
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "tags": ["test_tag"],
#                     },
#                     {
#                         "unique_id": "another-included-model",
#                         "tags": ["another_tag"],
#                     },
#                 ],
#             ]
#         ),
#         (
#             [
#                 [
#                     {
#                         "unique_id": "excluded-model",
#                         "tags": ["test_tag", "another_tag"],
#                     },
#                 ],
#                 ["test_tag"],
#                 ["another_tag"],
#                 [],
#             ]
#         ),
#         (
#             [
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "tags": ["test_tag"],
#                     },
#                     {
#                         "unique_id": "another-included-model",
#                         "tags": ["another_tag"],
#                     },
#                 ],
#                 None,
#                 None,
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "tags": ["test_tag"],
#                     },
#                     {
#                         "unique_id": "another-included-model",
#                         "tags": ["another_tag"],
#                     },
#                 ],
#             ]
#         ),
#         (
#             [
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "config": {"tags": ["test_tag"]},
#                     },
#                 ],
#                 ["test_tag"],
#                 None,
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "config": {"tags": ["test_tag"]},
#                     },
#                 ],
#             ]
#         ),
#         (
#             [
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "tags": ["tag1", "tag2", "tag3"],
#                     },
#                 ],
#                 ["tag1", "tag2", "tag3"],
#                 None,
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "tags": ["tag1", "tag2", "tag3"],
#                     },
#                 ],
#             ]
#         ),
#         (
#             [
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "tags": ["tag1", "tag2"],
#                     },
#                 ],
#                 ["tag1", "tag2", "tag3"],
#                 None,
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "tags": ["tag1", "tag2"],
#                     },
#                 ],
#             ]
#         ),
#     ],
# )
# def test_filter_nodes_by_tag(
#     nodes: Iterable[dict],
#     include_tags: list[str],
#     exclude_tags: list[str],
#     expected_return: Generator[dict, None, None],
# ):
#     actual_return = filter_nodes_by_tag(iter(nodes), include_tags, exclude_tags)
#     assert list(actual_return) == expected_return
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
#
#
# @pytest.mark.parametrize(
#     argnames=[
#         "nodes",
#         "include_paths",
#         "exclude_paths",
#         "expected_return",
#     ],
#     ids=[
#         "One node in an included path",
#         "One node in an included path, one out of scope",
#         "Two nodes, both with different included path",
#         "One included, one excluded, one omitted",
#         "No filter",
#     ],
#     argvalues=[
#         (
#             [
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "original_file_path": "test/model/path",
#                     },
#                 ],
#                 [Path("test/model")],
#                 None,
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "original_file_path": "test/model/path",
#                     },
#                 ],
#             ]
#         ),
#         (
#             [
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "original_file_path": "test/model/path",
#                     },
#                     {
#                         "unique_id": "excluded-model",
#                         "original_file_path": "test/another/path",
#                     },
#                 ],
#                 [Path("test/model/path")],
#                 None,
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "original_file_path": "test/model/path",
#                     },
#                 ],
#             ]
#         ),
#         (
#             [
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "original_file_path": "test/model/path",
#                     },
#                     {
#                         "unique_id": "another-included-model",
#                         "original_file_path": "test/another/path",
#                     },
#                 ],
#                 [Path("test/model/path"), Path("test/another/path")],
#                 None,
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "original_file_path": "test/model/path",
#                     },
#                     {
#                         "unique_id": "another-included-model",
#                         "original_file_path": "test/another/path",
#                     },
#                 ],
#             ]
#         ),
#         (
#             [
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "original_file_path": "test/model/path",
#                     },
#                     {
#                         "unique_id": "excluded-model",
#                         "original_file_path": "test/another/path",
#                     },
#                     {
#                         "unique_id": "omitted-model",
#                         "original_file_path": "test/one/more/path",
#                     },
#                 ],
#                 [Path("test/model")],
#                 [Path("test/another")],
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "original_file_path": "test/model/path",
#                     },
#                 ],
#             ]
#         ),
#         (
#             [
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "original_file_path": "test/model/path",
#                     },
#                     {
#                         "unique_id": "another-included-model",
#                         "original_file_path": "test/another/path",
#                     },
#                 ],
#                 None,
#                 None,
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "original_file_path": "test/model/path",
#                     },
#                     {
#                         "unique_id": "another-included-model",
#                         "original_file_path": "test/another/path",
#                     },
#                 ],
#             ]
#         ),
#     ],
# )
# def test_filter_nodes_by_path(
#     nodes: Iterable[dict],
#     include_paths: list[Path],
#     exclude_paths: list[Path],
#     expected_return: Generator[dict, None, None],
# ):
#     actual_return = filter_nodes_by_path(
#         iter(nodes), include_paths=include_paths, exclude_paths=exclude_paths
#     )
#     assert list(actual_return) == expected_return
#
#
# @pytest.mark.parametrize(
#     argnames=[
#         "nodes",
#         "include_resource_types",
#         "exclude_resource_types",
#         "expected_return",
#     ],
#     ids=[
#         "One node included",
#         "One node included, one omitted",
#         "Resource type not found in manifest",
#         "Two nodes, both with different included resource types",
#         "One included, one excluded, one omitted",
#         "No filter",
#     ],
#     argvalues=[
#         (
#             [
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "resource_type": "model",
#                     },
#                 ],
#                 ["model"],
#                 None,
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "resource_type": "model",
#                     },
#                 ],
#             ]
#         ),
#         (
#             [
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "resource_type": "model",
#                     },
#                     {
#                         "unique_id": "excluded-test",
#                         "resource_type": "test",
#                     },
#                 ],
#                 ["model"],
#                 None,
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "resource_type": "model",
#                     },
#                 ],
#             ]
#         ),
#         (
#             [
#                 [
#                     {
#                         "unique_id": "excluded-model",
#                         "resource_type": "model",
#                     },
#                 ],
#                 ["test"],
#                 None,
#                 [],
#             ]
#         ),
#         (
#             [
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "resource_type": "model",
#                     },
#                     {
#                         "unique_id": "included-test",
#                         "resource_type": "test",
#                     },
#                 ],
#                 ["model", "test"],
#                 None,
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "resource_type": "model",
#                     },
#                     {
#                         "unique_id": "included-test",
#                         "resource_type": "test",
#                     },
#                 ],
#             ]
#         ),
#         (
#             [
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "resource_type": "model",
#                     },
#                     {
#                         "unique_id": "excluded-test",
#                         "resource_type": "test",
#                     },
#                     {
#                         "unique_id": "omitted-model",
#                         "resource_type": "seed",
#                     },
#                 ],
#                 ["model"],
#                 ["test"],
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "resource_type": "model",
#                     },
#                 ],
#             ]
#         ),
#         (
#             [
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "resource_type": "model",
#                     },
#                     {
#                         "unique_id": "included-test",
#                         "resource_type": "test",
#                     },
#                     {
#                         "unique_id": "included-seed",
#                         "resource_type": "seed",
#                     },
#                 ],
#                 None,
#                 None,
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "resource_type": "model",
#                     },
#                     {
#                         "unique_id": "included-test",
#                         "resource_type": "test",
#                     },
#                     {
#                         "unique_id": "included-seed",
#                         "resource_type": "seed",
#                     },
#                 ],
#             ]
#         ),
#     ],
# )
# def test_filter_nodes_by_resource_type(
#     nodes: Iterable[dict],
#     include_resource_types: list[str],
#     exclude_resource_types: list[str],
#     expected_return: Generator[dict, None, None],
# ):
#     actual_return = filter_nodes_by_resource_type(
#         iter(nodes), include_resource_types, exclude_resource_types
#     )
#     assert list(actual_return) == expected_return
#
#
# @pytest.mark.parametrize(
#     ids=[
#         "Two included macros",
#         "One included, one excluded, one omitted",
#         "No filter",
#     ],
#     argnames=["nodes", "filter_condition", "expected_macros"],
#     argvalues=[
#         (
#             [
#                 [
#                     {
#                         "unique_id": "included-macro",
#                         "package_name": "test_dbt_package",
#                     },
#                     {
#                         "unique_id": "another-included-macro",
#                         "package_name": "test_dbt_package",
#                     },
#                 ],
#                 ManifestFilterConditions(include_packages=["test_dbt_package"]),
#                 [
#                     {
#                         "unique_id": "included-macro",
#                         "package_name": "test_dbt_package",
#                     },
#                     {
#                         "unique_id": "another-included-macro",
#                         "package_name": "test_dbt_package",
#                     },
#                 ],
#             ]
#         ),
#         (
#             [
#                 [
#                     {
#                         "unique_id": "included-macro",
#                         "package_name": "test_dbt_package",
#                     },
#                     {
#                         "unique_id": "excluded-macro",
#                         "package_name": "another_dbt_package",
#                     },
#                     {
#                         "unique_id": "omitted-macro",
#                         "package_name": "one_more_dbt_package",
#                     },
#                 ],
#                 ManifestFilterConditions(
#                     include_packages=["test_dbt_package"],
#                     exclude_packages=["another_dbt_package"],
#                 ),
#                 [
#                     {
#                         "unique_id": "included-macro",
#                         "package_name": "test_dbt_package",
#                     },
#                 ],
#             ]
#         ),
#         (
#             [
#                 [
#                     {
#                         "unique_id": "included-macro",
#                         "package_name": "test_dbt_package",
#                     },
#                     {
#                         "unique_id": "excluded-macro",
#                         "package_name": "another_dbt_package",
#                     },
#                     {
#                         "unique_id": "omitted-macro",
#                         "package_name": "one_more_dbt_package",
#                     },
#                 ],
#                 ManifestFilterConditions(),
#                 [
#                     {
#                         "unique_id": "included-macro",
#                         "package_name": "test_dbt_package",
#                     },
#                     {
#                         "unique_id": "excluded-macro",
#                         "package_name": "another_dbt_package",
#                     },
#                     {
#                         "unique_id": "omitted-macro",
#                         "package_name": "one_more_dbt_package",
#                     },
#                 ],
#             ]
#         ),
#     ],
# )
# def test_get_macros_from_manifest(
#     nodes: list[dict[str, str]],
#     filter_condition: ManifestFilterConditions,
#     expected_macros: list[dict[str, str]],
# ):
#     with patch(
#         "utils.artifact_data.get_json_artifact_data",
#         return_value={
#             "macros": {node["unique_id"]: node for node in nodes},
#             "not_macros": "",
#         },
#     ) as mock_get_json_artifact_data:
#         assert expected_macros == list(
#             get_in_scope_macros_from_manifest(Path(), filter_condition)
#         )
#         mock_get_json_artifact_data.assert_called_with(Path("manifest.json"))
#
#
# @pytest.mark.parametrize(
#     ids=[
#         "Two included",
#         "One included, one excluded, one omitted",
#         "No filter",
#         "One source with an included tag and an excluded tag",
#     ],
#     argnames=["nodes", "filter_condition", "expected_sources"],
#     argvalues=[
#         (
#             [
#                 [
#                     {
#                         "unique_id": "included-source",
#                         "package_name": "test_dbt_package",
#                         "tags": ["test_tag"],
#                         "original_file_path": "test/model/path",
#                     },
#                     {
#                         "unique_id": "another-included-source",
#                         "package_name": "test_dbt_package",
#                         "tags": ["test_tag"],
#                         "original_file_path": "test/another/path",
#                     },
#                 ],
#                 ManifestFilterConditions(
#                     include_packages=["test_dbt_package"],
#                     include_tags=["test_tag"],
#                     include_paths=[
#                         Path("test/model/path"),
#                         Path("test/another/path"),
#                     ],
#                 ),
#                 [
#                     {
#                         "unique_id": "included-source",
#                         "package_name": "test_dbt_package",
#                         "tags": ["test_tag"],
#                         "original_file_path": "test/model/path",
#                     },
#                     {
#                         "unique_id": "another-included-source",
#                         "package_name": "test_dbt_package",
#                         "tags": ["test_tag"],
#                         "original_file_path": "test/another/path",
#                     },
#                 ],
#             ]
#         ),
#         (
#             [
#                 [
#                     {
#                         "unique_id": "included-source",
#                         "package_name": "test_dbt_package",
#                         "tags": ["test_tag"],
#                         "original_file_path": "test/model/path",
#                     },
#                     {
#                         "unique_id": "excluded-source",
#                         "package_name": "another_dbt_package",
#                         "tags": ["test_tag"],
#                         "original_file_path": "test/another/path",
#                     },
#                     {
#                         "unique_id": "omitted-source",
#                         "package_name": "one_more_dbt_package",
#                         "tags": ["test_tag"],
#                         "original_file_path": "test/one/more/path",
#                     },
#                 ],
#                 ManifestFilterConditions(
#                     include_packages=["test_dbt_package"],
#                     exclude_packages=["another_dbt_package"],
#                 ),
#                 [
#                     {
#                         "unique_id": "included-source",
#                         "package_name": "test_dbt_package",
#                         "tags": ["test_tag"],
#                         "original_file_path": "test/model/path",
#                     },
#                 ],
#             ]
#         ),
#         (
#             [
#                 [
#                     {
#                         "unique_id": "included-source",
#                         "package_name": "test_dbt_package",
#                         "tags": ["test_tag"],
#                         "original_file_path": "test/model/path",
#                     },
#                     {
#                         "unique_id": "another-included-source",
#                         "package_name": "another_dbt_package",
#                         "tags": ["test_tag"],
#                         "original_file_path": "test/another/path",
#                     },
#                     {
#                         "unique_id": "one-more-included-source",
#                         "package_name": "one_more_dbt_package",
#                         "tags": ["test_tag"],
#                         "original_file_path": "test/one/more/path",
#                     },
#                 ],
#                 ManifestFilterConditions(),
#                 [
#                     {
#                         "unique_id": "included-source",
#                         "package_name": "test_dbt_package",
#                         "tags": ["test_tag"],
#                         "original_file_path": "test/model/path",
#                     },
#                     {
#                         "unique_id": "another-included-source",
#                         "package_name": "another_dbt_package",
#                         "tags": ["test_tag"],
#                         "original_file_path": "test/another/path",
#                     },
#                     {
#                         "unique_id": "one-more-included-source",
#                         "package_name": "one_more_dbt_package",
#                         "tags": ["test_tag"],
#                         "original_file_path": "test/one/more/path",
#                     },
#                 ],
#             ]
#         ),
#         (
#             [
#                 [
#                     {
#                         "unique_id": "excluded-source",
#                         "package_name": "test_dbt_package",
#                         "tags": ["included_tag", "excluded_tag"],
#                         "original_file_path": "test/model/path",
#                     },
#                 ],
#                 ManifestFilterConditions(
#                     include_tags=["included_tag"], exclude_tags=["excluded_tag"]
#                 ),
#                 [],
#             ]
#         ),
#     ],
# )
# def test_get_sources_from_manifest(
#     nodes: list[dict[str, str]],
#     filter_condition: ManifestFilterConditions,
#     expected_sources: list[dict[str, str]],
# ):
#     with patch(
#         "utils.artifact_data.get_json_artifact_data",
#         return_value={
#             "sources": {node["unique_id"]: node for node in nodes},
#             "not_sources": "",
#         },
#     ) as mock_get_json_artifact_data:
#         assert expected_sources == list(
#             get_in_scope_sources_from_manifest(Path(), filter_condition)
#         )
#         mock_get_json_artifact_data.assert_called_with(Path("manifest.json"))
#
#
# @pytest.mark.parametrize(
#     ids=[
#         "Two included",
#         "One included, one excluded, one omitted",
#         "No filter",
#         "One source with an included tag and an excluded tag",
#     ],
#     argnames=["nodes", "filter_condition", "expected_nodes"],
#     argvalues=[
#         (
#             [
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "package_name": "test_dbt_package",
#                         "tags": ["test_tag"],
#                         "original_file_path": "test/model/path",
#                     },
#                     {
#                         "unique_id": "included-test",
#                         "package_name": "test_dbt_package",
#                         "tags": ["test_tag"],
#                         "original_file_path": "test/another/path",
#                     },
#                 ],
#                 ManifestFilterConditions(
#                     include_packages=["test_dbt_package"],
#                     include_tags=["test_tag"],
#                     include_paths=[
#                         Path("test/model/path"),
#                         Path("test/another/path"),
#                     ],
#                 ),
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "package_name": "test_dbt_package",
#                         "tags": ["test_tag"],
#                         "original_file_path": "test/model/path",
#                     },
#                     {
#                         "unique_id": "included-test",
#                         "package_name": "test_dbt_package",
#                         "tags": ["test_tag"],
#                         "original_file_path": "test/another/path",
#                     },
#                 ],
#             ]
#         ),
#         (
#             [
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "package_name": "test_dbt_package",
#                         "tags": ["test_tag"],
#                         "original_file_path": "test/model/path",
#                     },
#                     {
#                         "unique_id": "excluded-test",
#                         "package_name": "another_dbt_package",
#                         "tags": ["test_tag"],
#                         "original_file_path": "test/another/path",
#                     },
#                     {
#                         "unique_id": "omitted-seed",
#                         "package_name": "one_more_dbt_package",
#                         "tags": ["test_tag"],
#                         "original_file_path": "test/one/more/path",
#                     },
#                 ],
#                 ManifestFilterConditions(
#                     include_packages=["test_dbt_package"],
#                     exclude_packages=["another_dbt_package"],
#                 ),
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "package_name": "test_dbt_package",
#                         "tags": ["test_tag"],
#                         "original_file_path": "test/model/path",
#                     },
#                 ],
#             ]
#         ),
#         (
#             [
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "package_name": "test_dbt_package",
#                         "tags": ["test_tag"],
#                         "original_file_path": "test/model/path",
#                     },
#                     {
#                         "unique_id": "included-test",
#                         "package_name": "another_dbt_package",
#                         "tags": ["test_tag"],
#                         "original_file_path": "test/another/path",
#                     },
#                     {
#                         "unique_id": "included-seed",
#                         "package_name": "one_more_dbt_package",
#                         "tags": ["test_tag"],
#                         "original_file_path": "test/one/more/path",
#                     },
#                 ],
#                 ManifestFilterConditions(),
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "package_name": "test_dbt_package",
#                         "tags": ["test_tag"],
#                         "original_file_path": "test/model/path",
#                     },
#                     {
#                         "unique_id": "included-test",
#                         "package_name": "another_dbt_package",
#                         "tags": ["test_tag"],
#                         "original_file_path": "test/another/path",
#                     },
#                     {
#                         "unique_id": "included-seed",
#                         "package_name": "one_more_dbt_package",
#                         "tags": ["test_tag"],
#                         "original_file_path": "test/one/more/path",
#                     },
#                 ],
#             ]
#         ),
#         (
#             [
#                 [
#                     {
#                         "unique_id": "excluded-model",
#                         "package_name": "test_dbt_package",
#                         "tags": ["included_tag", "excluded_tag"],
#                         "original_file_path": "test/model/path",
#                     },
#                 ],
#                 ManifestFilterConditions(
#                     include_tags=["included_tag"], exclude_tags=["excluded_tag"]
#                 ),
#                 [],
#             ]
#         ),
#     ],
# )
# def test_get_nodes_from_manifest(
#     nodes: list[dict[str, str]],
#     filter_condition: ManifestFilterConditions,
#     expected_nodes: list[dict[str, str]],
# ):
#     with patch(
#         "utils.artifact_data.get_json_artifact_data",
#         return_value={
#             "nodes": {node["unique_id"]: node for node in nodes},
#             "not_nodes": "",
#         },
#     ) as mock_get_json_artifact_data:
#         assert expected_nodes == list(
#             get_all_nodes_from_manifest(Path(), filter_condition)
#         )
#         mock_get_json_artifact_data.assert_called_with(Path("manifest.json"))
#
#
# @pytest.mark.parametrize(
#     ids=[
#         "Two included",
#         "One included, one excluded, one omitted",
#         "No filter",
#         "One source with an included tag and an excluded tag",
#     ],
#     argnames=["nodes", "filter_condition", "expected_nodes"],
#     argvalues=[
#         (
#             [
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "package_name": "test_dbt_package",
#                         "tags": ["test_tag"],
#                         "resource_type": "model",
#                     },
#                     {
#                         "unique_id": "another-included-model",
#                         "package_name": "test_dbt_package",
#                         "tags": ["test_tag"],
#                         "resource_type": "model",
#                     },
#                 ],
#                 ManifestFilterConditions(
#                     include_packages=["test_dbt_package"], include_tags=["test_tag"]
#                 ),
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "package_name": "test_dbt_package",
#                         "tags": ["test_tag"],
#                         "resource_type": "model",
#                     },
#                     {
#                         "unique_id": "another-included-model",
#                         "package_name": "test_dbt_package",
#                         "tags": ["test_tag"],
#                         "resource_type": "model",
#                     },
#                 ],
#             ]
#         ),
#         (
#             [
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "package_name": "test_dbt_package",
#                         "tags": ["test_tag"],
#                         "resource_type": "model",
#                     },
#                     {
#                         "unique_id": "excluded-model",
#                         "package_name": "another_dbt_package",
#                         "tags": ["test_tag"],
#                         "resource_type": "model",
#                     },
#                     {
#                         "unique_id": "omitted-model",
#                         "package_name": "one_more_dbt_package",
#                         "tags": ["test_tag"],
#                         "resource_type": "model",
#                     },
#                 ],
#                 ManifestFilterConditions(
#                     include_packages=["test_dbt_package"],
#                     exclude_packages=["another_dbt_package"],
#                 ),
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "package_name": "test_dbt_package",
#                         "tags": ["test_tag"],
#                         "resource_type": "model",
#                     },
#                 ],
#             ]
#         ),
#         (
#             [
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "package_name": "test_dbt_package",
#                         "tags": ["test_tag"],
#                         "resource_type": "model",
#                     },
#                     {
#                         "unique_id": "another-included-model",
#                         "package_name": "another_dbt_package",
#                         "tags": ["test_tag"],
#                         "resource_type": "model",
#                     },
#                     {
#                         "unique_id": "one-more-included-model",
#                         "package_name": "one_more_dbt_package",
#                         "tags": ["test_tag"],
#                         "resource_type": "model",
#                     },
#                 ],
#                 ManifestFilterConditions(),
#                 [
#                     {
#                         "unique_id": "included-model",
#                         "package_name": "test_dbt_package",
#                         "tags": ["test_tag"],
#                         "resource_type": "model",
#                     },
#                     {
#                         "unique_id": "another-included-model",
#                         "package_name": "another_dbt_package",
#                         "tags": ["test_tag"],
#                         "resource_type": "model",
#                     },
#                     {
#                         "unique_id": "one-more-included-model",
#                         "package_name": "one_more_dbt_package",
#                         "tags": ["test_tag"],
#                         "resource_type": "model",
#                     },
#                 ],
#             ]
#         ),
#         (
#             [
#                 [
#                     {
#                         "unique_id": "excluded-model",
#                         "package_name": "test_dbt_package",
#                         "tags": ["included_tag", "excluded_tag"],
#                         "resource_type": "model",
#                     },
#                 ],
#                 ManifestFilterConditions(
#                     include_tags=["included_tag"], exclude_tags=["excluded_tag"]
#                 ),
#                 [],
#             ]
#         ),
#     ],
# )
# def test_get_models_from_manifest(
#     nodes: list[dict[str, str]],
#     filter_condition: ManifestFilterConditions,
#     expected_nodes: list[dict[str, str]],
# ):
#     with patch(
#         "utils.artifact_data.get_json_artifact_data",
#         return_value={
#             "nodes": {node["unique_id"]: node for node in nodes},
#             "not_nodes": "",
#         },
#     ) as mock_get_json_artifact_data:
#         assert expected_nodes == list(
#             get_in_scope_models_from_manifest(
#                 manifest_dir=Path(), filter_conditions=filter_condition
#             )
#         )
#         mock_get_json_artifact_data.assert_called_with(Path("manifest.json"))
#
#
# @pytest.mark.parametrize(
#     ids=["base case", "Empty/None"],
#     argnames=["kwargs", "expected_attributes"],
#     argvalues=[
#         (
#             {
#                 "include_materializations": ("table", "view"),
#                 "include_packages": ["test_dbt_project", "another_dbt_project"],
#                 "include_tags": {"test_tag", "another_tag"},
#                 "include_node_paths": {
#                     Path("test/model/path"),
#                     Path("test/another/path"),
#                 },
#                 "exclude_materializations": ("ephemeral", "incremental"),
#                 "exclude_packages": ["one_more_dbt_project"],
#                 "exclude_tags": {"one_more_tag"},
#                 "exclude_node_paths": {Path("test/one/more/path")},
#             },
#             {
#                 "include_materializations": {"table", "view"},
#                 "include_packages": {"test_dbt_project", "another_dbt_project"},
#                 "include_tags": {"test_tag", "another_tag"},
#                 "include_node_paths": {
#                     Path("test/model/path"),
#                     Path("test/another/path"),
#                 },
#                 "exclude_materializations": {"ephemeral", "incremental"},
#                 "exclude_packages": {"one_more_dbt_project"},
#                 "exclude_tags": {"one_more_tag"},
#                 "exclude_node_paths": {Path("test/one/more/path")},
#             },
#         ),
#         (
#             {
#                 "include_materializations": (),
#                 "include_packages": None,
#                 "include_tags": None,
#                 "include_node_paths": None,
#                 "exclude_materializations": [],
#                 "exclude_packages": set(),
#                 "exclude_tags": None,
#                 "exclude_node_paths": None,
#             },
#             {
#                 "include_materializations": None,
#                 "include_packages": None,
#                 "include_tags": None,
#                 "include_node_paths": None,
#                 "exclude_materializations": None,
#                 "exclude_packages": None,
#                 "exclude_tags": None,
#                 "exclude_node_paths": None,
#             },
#         ),
#     ],
# )
# def test_manifest_filter_conditions_init(kwargs, expected_attributes):
#     for attribute_name, attribute_value in expected_attributes.items():
#         assert (
#             getattr(ManifestFilterConditions(**kwargs), attribute_name)
#             == attribute_value
#         )
#
#
# @pytest.mark.parametrize(
#     ids=["base case", "Empty/None"],
#     argnames=["kwargs", "expected_summary"],
#     argvalues=[
#         (
#             {
#                 "include_materializations": ("table", "view"),
#                 "include_packages": ["test_dbt_project", "another_dbt_project"],
#                 "include_tags": {"test_tag", "another_tag"},
#                 "include_node_paths": {
#                     Path("test/model/path"),
#                     Path("test/another/path"),
#                 },
#                 "exclude_materializations": ("ephemeral", "incremental"),
#                 "exclude_packages": ["one_more_dbt_project"],
#                 "exclude_tags": {"one_more_tag"},
#                 "exclude_node_paths": {Path("test/one/more/path")},
#             },
#             colour_message(
#                 """Including:
# 	materialized: table, view
# 	tags: another_tag, test_tag
# 	packages: another_dbt_project, test_dbt_project
# 	node paths: test/another/path, test/model/path
# Excluding:
# 	materialized: ephemeral, incremental
# 	tags: one_more_tag
# 	packages: one_more_dbt_project
# 	node paths: test/one/more/path""",
#                 emphasis=ConsoleEmphasis.ITALIC,
#             ),
#         ),
#         (
#             {
#                 "include_materializations": (),
#                 "include_packages": None,
#                 "include_tags": None,
#                 "include_node_paths": None,
#                 "exclude_materializations": [],
#                 "exclude_packages": set(),
#                 "exclude_tags": None,
#                 "exclude_node_paths": None,
#             },
#             colour_message("", emphasis=ConsoleEmphasis.ITALIC),
#         ),
#     ],
# )
# def test_manifest_filter_conditions_summary(kwargs, expected_summary):
#     assert ManifestFilterConditions(**kwargs).summary == expected_summary
#
#
# @pytest.mark.parametrize(
#     ids=["same", "different"],
#     argnames=["instance_1", "instance_2", "expected_return"],
#     argvalues=[
#         (
#             ManifestFilterConditions(
#                 include_materializations=("table", "view"),
#                 include_packages=("test_dbt_project", "another_dbt_project"),
#                 include_tags=("test_tag", "another_tag"),
#                 include_paths=(Path("test/model/path"), Path("test/another/path")),
#                 exclude_materializations=("ephemeral", "incremental"),
#                 exclude_packages=("one_more_dbt_project",),
#                 exclude_tags=("one_more_tag",),
#                 exclude_paths=(Path("test/one/more/path"),),
#             ),
#             ManifestFilterConditions(
#                 include_materializations=("table", "view"),
#                 include_packages=("test_dbt_project", "another_dbt_project"),
#                 include_tags=("test_tag", "another_tag"),
#                 include_paths=(Path("test/model/path"), Path("test/another/path")),
#                 exclude_materializations=("ephemeral", "incremental"),
#                 exclude_packages=("one_more_dbt_project",),
#                 exclude_tags=("one_more_tag",),
#                 exclude_paths=(Path("test/one/more/path"),),
#             ),
#             True,
#         ),
#         (
#             ManifestFilterConditions(
#                 include_materializations=("table", "view"),
#                 include_packages=("test_dbt_project", "another_dbt_project"),
#                 include_tags=("test_tag", "another_tag"),
#                 include_paths=(Path("test/model/path"), Path("test/another/path")),
#                 exclude_materializations=("ephemeral", "incremental"),
#                 exclude_packages=("one_more_dbt_project",),
#                 exclude_tags=("one_more_tag",),
#                 exclude_paths=(Path("test/one/more/path"),),
#             ),
#             ManifestFilterConditions(
#                 include_materializations=("table", "view"),
#             ),
#             False,
#         ),
#     ],
# )
# def test_manifest_filter_conditions_eq(
#     instance_1: ManifestFilterConditions,
#     instance_2: ManifestFilterConditions,
#     expected_return: bool,
# ):
#     assert (instance_1 == instance_2) is expected_return
#
#
# @pytest.mark.parametrize(
#     ids=[
#         "direct tags list and config tags list",
#         "direct tag string and config tag string",
#         "no tags",
#     ],
#     argnames=["manifest_object", "expected_return"],
#     argvalues=[
#         (
#             {
#                 "tags": ["tag_1", "tag_2"],
#                 "config": {"tags": ["tag_3", "tag_4"]},
#             },
#             {"tag_1", "tag_2", "tag_3", "tag_4"},
#         ),
#         (
#             {
#                 "tags": "tag_1",
#                 "config": {"tags": "tag_2"},
#             },
#             {"tag_1", "tag_2"},
#         ),
#         ({}, set()),
#     ],
# )
# def test_get_tags_for_manifest_object(
#     manifest_object: dict[str, Any], expected_return: set[str]
# ):
#     assert expected_return == get_tags_for_manifest_object(manifest_object)
