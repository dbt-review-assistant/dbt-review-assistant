"""Utilities for fetching dbt artifact data."""

import json
import warnings
from functools import cached_property, lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Any, Collection

from utils.catalog_object.catalog_table import CatalogTable
from utils.manifest_object.macro import Macro
from utils.manifest_object.manifest_object import ManifestColumn, ManifestSource
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

if TYPE_CHECKING:
    from utils.manifest_filter_conditions import ManifestFilterConditions


MANIFEST_FILE_NAME = "manifest.json"
CATALOG_FILE_NAME = "catalog.json"
SUPPORTED_MANIFEST_SCHEMA_VERSION = "https://schemas.getdbt.com/dbt/manifest/v12.json"
SUPPORTED_CATALOG_SCHEMA_VERSION = "https://schemas.getdbt.com/dbt/catalog/v1.json"


class Catalog:
    """Represents the data in the dbt catalog.json file."""

    def __init__(self, catalog_dir: Path):
        """Initialise the instance.

        Args:
            catalog_dir: directory where the catalog.json file is located.
        """
        self.data = get_json_artifact_data(catalog_dir / CATALOG_FILE_NAME)
        schema_version = self.data.get("metadata", {}).get("dbt_schema_version")
        if schema_version != SUPPORTED_CATALOG_SCHEMA_VERSION:
            warnings.warn(
                f"Unsupported catalog schema version: '{schema_version}'. "
                f"Only '{SUPPORTED_CATALOG_SCHEMA_VERSION}' (dbt Core 1.0+) is explicitly supported. "
                "To resolve, upgrade to dbt Core 1.0 or later and re-run `dbt docs generate` to regenerate the catalog. "
                "Results may be incorrect or incomplete.",
                UserWarning,
                stacklevel=2,
            )

    @cached_property
    def nodes(self) -> dict[str, CatalogTable]:
        """All nodes present in the catalog.

        Returns:
            a dictionary mapping unique IDs to CatalogTable objects.
        """
        return {
            node_id: CatalogTable(node_data)
            for node_id, node_data in self.data.get("nodes", {}).items()
        }

    @cached_property
    def sources(self) -> dict[str, CatalogTable]:
        """All sources present in the catalog.

        Returns:
            a dictionary mapping unique IDs to CatalogTable objects.
        """
        return {
            source_id: CatalogTable(source_data)
            for source_id, source_data in self.data.get("sources", {}).items()
        }


class Manifest:
    """Represents the data in the dbt manifest.json file."""

    def __init__(
        self,
        manifest_dir: Path,
        filter_conditions: "ManifestFilterConditions",
        filepaths: Collection[Path] | None = None,
    ):
        """Initialise the instance.

        Args:
            manifest_dir: directory where the manifest.json file is located.
            filter_conditions: A ManifestFilterConditions object to filter nodes by.
            filepaths: Collection of Path objects representing the files to include.
        """
        self.data = get_json_artifact_data(manifest_dir / MANIFEST_FILE_NAME)
        self.filter_conditions = filter_conditions
        self.filepaths = set(filepaths) if filepaths else None
        schema_version = self.data.get("metadata", {}).get("dbt_schema_version")
        if schema_version != SUPPORTED_MANIFEST_SCHEMA_VERSION:
            warnings.warn(
                f"Unsupported manifest schema version: '{schema_version}'. "
                f"Only '{SUPPORTED_MANIFEST_SCHEMA_VERSION}' (dbt Core 1.8+) is explicitly supported. "
                "Manifest schema versions by dbt release: v12 → 1.8+, v11 → 1.7, v10 → 1.6, v9 → 1.5. "
                "To resolve, upgrade to dbt Core 1.8 or later and re-run `dbt parse` to regenerate the manifest. "
                "Results may be incorrect or incomplete.",
                UserWarning,
                stacklevel=2,
            )

    @cached_property
    def nodes(self) -> dict[str, dict[str, Any]]:
        """All nodes present in the manifest.

        Returns:
            a data from the 'nodes' section of the manifest.json file.
        """
        return self.data.get("nodes", {})

    @cached_property
    def models(self) -> dict[str, ManifestModel]:
        """All models present in the manifest.

        Returns:
            a dictionary mapping unique IDs to ManifestModel objects.
        """
        return {
            node_id: ManifestModel(data=node_data)
            for node_id, node_data in self.nodes.items()
            if node_data.get("resource_type") == "model"
        }

    @cached_property
    def in_scope_models(self) -> list[ManifestModel]:
        """All models present in the manifest, after filtering.

        Returns:
            List of ManifestModel objects after filtering.
        """
        return [
            model
            for model in self.models.values()
            if self.filter_conditions.is_manifest_object_in_scope(model, self)
            and (
                not self.filepaths
                or model.is_included_by_original_or_patch_path(self.filepaths)
            )
        ]

    @cached_property
    def in_scope_model_columns(self) -> list[ManifestColumn]:
        """All model columns present in the manifest, after filtering.

        Returns:
            List of ManifestColumn objects after filtering.
        """
        return [
            column
            for model in self.models.values()
            for column in model.columns
            if self.filter_conditions.is_manifest_object_in_scope(column, self)
        ]

    def get_model(self, model_id: str) -> ManifestModel | None:
        """Get a model from the manifest by looking up by unique ID.

        Args:
            model_id: unique id of the model

        Returns:
            A ManifestModel object if found, else None
        """
        return self.models.get(model_id)

    @cached_property
    def generic_tests(self) -> dict[str, GenericTest]:
        """All generic tests present in the manifest.

        Returns:
            a dictionary mapping unique IDs to GenericTest objects.
        """
        return {
            node_id: GenericTest(data=node_data)
            for node_id, node_data in self.nodes.items()
            if node_data.get("resource_type") == "test"
            and node_data.get("test_metadata")
        }

    @cached_property
    def snapshots(self) -> dict[str, ManifestSnapshot]:
        """All snapshots present in the manifest.

        Returns:
            a dictionary mapping unique IDs to ManifestSnapshot objects.
        """
        return {
            node_id: ManifestSnapshot(data=node_data)
            for node_id, node_data in self.nodes.items()
            if node_data.get("resource_type") == "snapshot"
        }

    @cached_property
    def seeds(self) -> dict[str, ManifestSeed]:
        """All seeds present in the manifest.

        Returns:
            a dictionary mapping unique IDs to ManifestSeed objects.
        """
        return {
            node_id: ManifestSeed(data=node_data)
            for node_id, node_data in self.nodes.items()
            if node_data.get("resource_type") == "seed"
        }

    @cached_property
    def analyses(self) -> dict[str, ManifestAnalysis]:
        """All analyses present in the manifest.

        Returns:
            a dictionary mapping unique IDs to ManifestAnalysis objects.
        """
        return {
            node_id: ManifestAnalysis(data=node_data)
            for node_id, node_data in self.nodes.items()
            if node_data.get("resource_type") == "analysis"
        }

    @cached_property
    def singular_tests(self) -> dict[str, SingularTest]:
        """All singular tests present in the manifest.

        Returns:
            a dictionary mapping unique IDs to SingularTest objects.
        """
        return {
            node_id: SingularTest(data=node_data)
            for node_id, node_data in self.nodes.items()
            if node_data.get("resource_type") == "test"
            and not node_data.get("test_metadata")
        }

    @cached_property
    def functions(self) -> dict[str, ManifestFunction]:
        """All functions present in the manifest.

        Returns:
            a dictionary mapping unique IDs to ManifestFunction objects.
        """
        return {
            node_id: ManifestFunction(data=node_data)
            for node_id, node_data in self.nodes.items()
            if node_data.get("resource_type") == "function"
        }

    @cached_property
    def sources(self) -> dict[str, ManifestSource]:
        """All sources present in the manifest.

        Returns:
            a dictionary mapping unique IDs to ManifestSource objects.
        """
        return {
            source_id: ManifestSource(source_data)
            for source_id, source_data in self.data.get("sources", {}).items()
        }

    @cached_property
    def in_scope_sources(self) -> list[ManifestSource]:
        """All sources present in the manifest, after filtering.

        Returns:
            List of ManifestSource objects after filtering.
        """
        return [
            source
            for source in self.sources.values()
            if self.filter_conditions.is_manifest_object_in_scope(source, self)
            and (
                not self.filepaths
                or source.is_included_by_original_or_patch_path(self.filepaths)
            )
        ]

    @cached_property
    def in_scope_source_columns(self) -> list[ManifestColumn]:
        """All source columns present in the manifest, after filtering.

        Returns:
            List of ManifestColumn objects after filtering.
        """
        return [
            column
            for source in self.sources.values()
            for column in source.columns
            if self.filter_conditions.is_manifest_object_in_scope(column, self)
        ]

    @cached_property
    def macros(self) -> dict[str, Macro]:
        """All macros present in the manifest.

        Returns:
            a dictionary mapping unique IDs to Macro objects.
        """
        return {
            macro_id: Macro(macro_data)
            for macro_id, macro_data in self.data.get("macros", {}).items()
        }

    @cached_property
    def in_scope_macros(self) -> list[Macro]:
        """All macros present in the manifest, after filtering.

        Returns:
            List of Macro instances after filtering.
        """
        return [
            macro
            for macro in self.macros.values()
            if self.filter_conditions.is_manifest_object_in_scope(macro, self)
            and (
                not self.filepaths
                or macro.is_included_by_original_or_patch_path(self.filepaths)
            )
        ]

    @cached_property
    def in_scope_snapshots(self) -> list[ManifestSnapshot]:
        """All snapshots present in the manifest, after filtering.

        Returns:
            List of ManifestSnapshot objects after filtering.
        """
        return [
            snapshot
            for snapshot in self.snapshots.values()
            if self.filter_conditions.is_manifest_object_in_scope(snapshot, self)
            and (
                not self.filepaths
                or snapshot.is_included_by_original_or_patch_path(self.filepaths)
            )
        ]

    @cached_property
    def in_scope_seeds(self) -> list[ManifestSeed]:
        """All seeds present in the manifest, after filtering.

        Returns:
            List of ManifestSeed objects after filtering.
        """
        seed_filepaths = (
            {p for p in self.filepaths if p.suffix == ".csv" or "seeds" in p.parts}
            if self.filepaths
            else None
        )
        return [
            seed
            for seed in self.seeds.values()
            if self.filter_conditions.is_manifest_object_in_scope(seed, self)
            and (
                not seed_filepaths
                or seed.is_included_by_original_or_patch_path(seed_filepaths)
            )
        ]

    @cached_property
    def in_scope_seed_columns(self) -> list[ManifestColumn]:
        """All seed columns present in the manifest, after filtering.

        Returns:
            List of ManifestColumn objects after filtering.
        """
        return [
            column
            for seed in self.seeds.values()
            for column in seed.columns
            if self.filter_conditions.is_manifest_object_in_scope(column, self)
        ]

    @cached_property
    def unit_tests(self) -> dict[str, UnitTest]:
        """All unit tests present in the manifest.

        Returns:
            a dictionary mapping unique IDs to UnitTest objects.
        """
        return {
            unit_test_id: UnitTest(unit_test_data)
            for unit_test_id, unit_test_data in self.data.get("unit_tests", {}).items()
        }

    @cached_property
    def child_map(self) -> dict[str, list[str]]:
        """Child map data from the manifest.

        Returns:
            a dictionary mapping unique IDs to lists of child IDs.
        """
        return self.data.get("child_map", {})

    @cached_property
    def parent_map(self) -> dict[str, list[str]]:
        """Parent map data from the manifest.

        Returns:
            a dictionary mapping unique IDs to lists of parent IDs.
        """
        return self.data.get("parent_map", {})


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
