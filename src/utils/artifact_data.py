"""Utilities for fetching dbt artifact data."""

import json
from pathlib import Path
from typing import Any, Generator
from functools import lru_cache

from utils.catalog_object.catalog_table import CatalogTable
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

MANIFEST_FILE_NAME = "manifest.json"
CATALOG_FILE_NAME = "catalog.json"


class Catalog:
    def __init__(self, catalog_dir: Path):
        self.data = get_json_artifact_data(catalog_dir / CATALOG_FILE_NAME)

    @property
    def nodes(self) -> dict[str, CatalogTable]:
        return {
            node_id: CatalogTable(node_data)
            for node_id, node_data in self.data.get("nodes", {}).items()
        }

    def get_node(self, node_id: str) -> CatalogTable | None:
        return self.nodes.get(node_id)

    @property
    def sources(self) -> dict[str, CatalogTable]:
        return {
            source_id: CatalogTable(source_data)
            for source_id, source_data in self.data.get("sources", {}).items()
        }

    def get_source(self, source_id: str) -> CatalogTable | None:
        return self.sources.get(source_id)


class Manifest:
    def __init__(
        self, manifest_dir: Path, filter_conditions: "ManifestFilterConditions"
    ):
        self.data = get_json_artifact_data(manifest_dir / MANIFEST_FILE_NAME)
        self.filter_conditions = filter_conditions

    @property
    def nodes(self) -> dict[str, dict[str, Any]]:
        return self.data.get("nodes", {})

    @property
    def models(self) -> dict[str, ManifestModel]:
        return {
            node_id: ManifestModel(
                data=node_data, filter_conditions=self.filter_conditions
            )
            for node_id, node_data in self.nodes.items()
            if node_data.get("resource_type") == "model"
        }

    @property
    def in_scope_models(self) -> Generator[ManifestModel, None, None]:
        return (model for model in self.models.values() if model.is_in_scope)

    def get_model(self, model_id: str) -> ManifestModel | None:
        return self.models.get(model_id)

    @property
    def generic_tests(self) -> dict[str, GenericTest]:
        return {
            node_id: GenericTest(
                data=node_data, filter_conditions=self.filter_conditions
            )
            for node_id, node_data in self.nodes.items()
            if node_data.get("resource_type") == "test"
        }

    def get_generic_test(self, test_id: str) -> GenericTest | None:
        return self.generic_tests.get(test_id)

    @property
    def snapshots(self) -> dict[str, ManifestSnapshot]:
        return {
            node_id: ManifestSnapshot(
                data=node_data, filter_conditions=self.filter_conditions
            )
            for node_id, node_data in self.nodes.items()
            if node_data.get("resource_type") == "snapshot"
        }

    @property
    def seeds(self) -> dict[str, ManifestSeed]:
        return {
            node_id: ManifestSeed(
                data=node_data, filter_conditions=self.filter_conditions
            )
            for node_id, node_data in self.nodes.items()
            if node_data.get("resource_type") == "seed"
        }

    @property
    def analyses(self) -> dict[str, ManifestAnalysis]:
        return {
            node_id: ManifestAnalysis(
                data=node_data, filter_conditions=self.filter_conditions
            )
            for node_id, node_data in self.nodes.items()
            if node_data.get("resource_type") == "analysis"
        }

    @property
    def singular_tests(self) -> dict[str, SingularTest]:
        return {
            node_id: SingularTest(
                data=node_data, filter_conditions=self.filter_conditions
            )
            for node_id, node_data in self.nodes.items()
            if node_data.get("resource_type") == "singular_test"
        }

    @property
    def functions(self) -> dict[str, ManifestFunction]:
        return {
            node_id: ManifestFunction(
                data=node_data, filter_conditions=self.filter_conditions
            )
            for node_id, node_data in self.nodes.items()
            if node_data.get("resource_type") == "function"
        }

    @property
    def sources(self) -> dict[str, ManifestSource]:
        return {
            source_id: ManifestSource(
                source_data, filter_conditions=self.filter_conditions
            )
            for source_id, source_data in self.data.get("sources").items()
        }

    @property
    def in_scope_sources(self) -> Generator[ManifestSource, None, None]:
        return (source for source in self.sources.values() if source.is_in_scope)

    def get_source(self, source_id: str) -> ManifestSource | None:
        return self.sources.get(source_id)

    @property
    def macros(self) -> dict[str, Macro]:
        return {
            macro_id: Macro(macro_data, filter_conditions=self.filter_conditions)
            for macro_id, macro_data in self.data.get("macros").items()
        }

    @property
    def in_scope_macros(self) -> Generator[Macro, None, None]:
        return (macro for macro in self.macros.values() if macro.is_in_scope)

    @property
    def unit_tests(self) -> dict[str, UnitTest]:
        return {
            unit_test_id: UnitTest(
                unit_test_data, filter_conditions=self.filter_conditions
            )
            for unit_test_id, unit_test_data in self.data.get("unit_tests").items()
        }

    def get_unit_test(self, unit_test_id: str) -> UnitTest | None:
        return self.unit_tests.get(unit_test_id)

    @property
    def child_map(self) -> dict[str, list[str] | None]:
        return self.data.get("child_map", {})


@lru_cache
def get_json_artifact_data(artifact_path: Path) -> dict:
    """Load data from a dbt JSON artifact.

    Args:
        artifact_path: Path to the dbt JSON artifact

    Returns:
        dbt artifact data as a dictionary

    Raises:
        FileNotFoundError: If artifact path does not exist
    """
    if not artifact_path.exists():
        raise FileNotFoundError(f"Path {artifact_path.absolute()} does not exist.")
    with open(artifact_path, "r") as file_handler:
        data = json.load(file_handler)
    return data
