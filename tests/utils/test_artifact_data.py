import json
from contextlib import nullcontext as does_not_raise
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from utils.artifact_data import (
    CATALOG_FILE_NAME,
    MANIFEST_FILE_NAME,
    Catalog,
    Manifest,
    get_json_artifact_data,
)
from utils.catalog_object.catalog_table import CatalogTable
from utils.manifest_filter_conditions import ManifestFilterConditions
from utils.manifest_object.macro import Macro
from utils.manifest_object.manifest_object import ManifestSource
from utils.manifest_object.node.generic_test import GenericTest
from utils.manifest_object.node.model.model import ManifestModel
from utils.manifest_object.node.node import (
    ManifestAnalysis,
    ManifestFunction,
    ManifestSeed,
    ManifestSnapshot,
    SingularTest,
)
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
    filters = ManifestFilterConditions(_include_packages=["test_package"])
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
            "test_test": {"resource_type": "test", "test_metadata": {"name": "test"}},
            "another_test": {
                "resource_type": "test",
                "test_metadata": {"name": "test"},
            },
            "singular_test": {"resource_type": "test"},
            "test_seed": {"resource_type": "seed"},
        },
        "sources": {},
        "unit_tests": {},
    }
    expected_tests = {
        "test_test": GenericTest(
            data={"resource_type": "test", "test_metadata": {"name": "test"}},
            filter_conditions=filters,
        ),
        "another_test": GenericTest(
            data={"resource_type": "test", "test_metadata": {"name": "test"}},
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
            "test_singular_test": {"resource_type": "test"},
            "another_singular_test": {"resource_type": "test"},
            "generic_test": {
                "resource_type": "test",
                "test_metadata": {"name": "test"},
            },
            "test_seed": {"resource_type": "seed"},
        },
        "sources": {},
        "unit_tests": {},
    }
    expected_singular_tests = {
        "test_singular_test": SingularTest(
            data={"resource_type": "test"},
            filter_conditions=filters,
        ),
        "another_singular_test": SingularTest(
            data={"resource_type": "test"},
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
    filters = ManifestFilterConditions(_include_packages=["test_package"])
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
    filters = ManifestFilterConditions(_include_packages=["test_package"])
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
