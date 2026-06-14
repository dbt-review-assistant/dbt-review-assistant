"""All pre-commit hooks."""

from checks.macro_checks.macro_arguments_have_descriptions import (
    MacroArgumentsHaveDescriptions,
)
from checks.macro_checks.macro_arguments_have_types import MacroArgumentsHaveTypes
from checks.macro_checks.macro_arguments_match_manifest_vs_sql import (
    MacroArgumentsMatchManifestVsSql,
)
from checks.macro_checks.macro_names_must_match_pattern import MacroNamesMatchPattern
from checks.macro_checks.macros_have_descriptions import MacrosHaveDescriptions
from checks.model_checks.model_column_descriptions_are_consistent import (
    ModelColumnsDescriptionsAreConsistent,
)
from checks.model_checks.model_column_names_match_manifest_vs_catalog import (
    ModelColumnNamesMatchManifestVsCatalog,
)
from checks.model_checks.model_column_names_must_match_pattern import (
    ModelColumnNamesMatchPattern,
)
from checks.model_checks.model_column_types_match_manifest_vs_catalog import (
    ModelColumnTypesMatchManifestVsCatalog,
)
from checks.model_checks.model_columns_have_descriptions import (
    ModelColumnsHaveDescriptions,
)
from checks.model_checks.model_columns_have_types import ModelColumnsHaveTypes
from checks.model_checks.model_names_must_match_pattern import ModelNamesMatchPattern
from checks.model_checks.models_have_access import ModelsHaveAccess
from checks.model_checks.models_have_columns import ModelsHaveColumns
from checks.model_checks.models_have_constraints import ModelsHaveConstraints
from checks.model_checks.models_have_contracts import ModelsHaveContracts
from checks.model_checks.models_have_data_tests import ModelsHaveDataTests
from checks.model_checks.models_have_descriptions import ModelsHaveDescriptions
from checks.model_checks.models_have_properties_file import ModelsHavePropertiesFile
from checks.model_checks.models_have_specific_config import ModelsHaveSpecificConfig
from checks.model_checks.models_have_specific_materialization import (
    ModelsHaveSpecificMaterialization,
)
from checks.model_checks.models_have_specific_meta import ModelsHaveSpecificMeta
from checks.model_checks.models_have_tags import ModelsHaveTags
from checks.model_checks.models_have_unit_tests import ModelsHaveUnitTests
from checks.seed_checks.seed_column_names_match_manifest_vs_catalog import (
    SeedColumnNamesMatchManifestVsCatalog,
)
from checks.seed_checks.seed_column_types_match_manifest_vs_catalog import (
    SeedColumnTypesMatchManifestVsCatalog,
)
from checks.seed_checks.seed_columns_have_descriptions import (
    SeedColumnsHaveDescriptions,
)
from checks.seed_checks.seed_columns_have_types import SeedColumnsHaveTypes
from checks.seed_checks.seeds_have_columns import SeedsHaveColumns
from checks.seed_checks.seeds_have_data_tests import SeedsHaveDataTests
from checks.seed_checks.seeds_have_descriptions import SeedsHaveDescriptions
from checks.seed_checks.seeds_have_tags import SeedsHaveTags
from checks.snapshot_checks.snapshot_columns_have_descriptions import (
    SnapshotColumnsHaveDescriptions,
)
from checks.snapshot_checks.snapshot_columns_have_types import SnapshotColumnsHaveTypes
from checks.snapshot_checks.snapshot_names_match_pattern import (
    SnapshotNamesMatchPattern,
)
from checks.snapshot_checks.snapshots_have_columns import SnapshotsHaveColumns
from checks.snapshot_checks.snapshots_have_data_tests import SnapshotsHaveDataTests
from checks.snapshot_checks.snapshots_have_descriptions import SnapshotsHaveDescriptions
from checks.snapshot_checks.snapshots_have_tags import SnapshotsHaveTags
from checks.source_checks.source_column_names_match_manifest_vs_catalog import (
    SourceColumnNamesMatchManifestVsCatalog,
)
from checks.source_checks.source_column_types_match_manifest_vs_catalog import (
    SourceColumnTypesMatchManifestVsCatalog,
)
from checks.source_checks.source_columns_have_descriptions import (
    SourceColumnsHaveDescriptions,
)
from checks.source_checks.source_columns_have_types import SourceColumnsHaveTypes
from checks.source_checks.sources_have_columns import SourcesHaveColumns
from checks.source_checks.sources_have_data_tests import SourcesHaveDataTests
from checks.source_checks.sources_have_descriptions import SourcesHaveDescriptions
from checks.source_checks.sources_have_freshness import SourcesHaveFreshness
from checks.source_checks.sources_have_loader import SourcesHaveLoader
from checks.source_checks.sources_have_tags import SourcesHaveTags

ALL_CHECKS = (
    MacroArgumentsHaveDescriptions,
    MacroArgumentsHaveTypes,
    MacroArgumentsMatchManifestVsSql,
    MacroNamesMatchPattern,
    MacrosHaveDescriptions,
    ModelColumnsDescriptionsAreConsistent,
    ModelColumnNamesMatchManifestVsCatalog,
    ModelColumnNamesMatchPattern,
    ModelColumnTypesMatchManifestVsCatalog,
    ModelColumnsHaveDescriptions,
    ModelColumnsHaveTypes,
    ModelNamesMatchPattern,
    ModelsHaveAccess,
    ModelsHaveColumns,
    ModelsHaveConstraints,
    ModelsHaveContracts,
    ModelsHaveDataTests,
    ModelsHaveDescriptions,
    ModelsHavePropertiesFile,
    ModelsHaveSpecificConfig,
    ModelsHaveSpecificMaterialization,
    ModelsHaveSpecificMeta,
    ModelsHaveTags,
    ModelsHaveUnitTests,
    SeedColumnNamesMatchManifestVsCatalog,
    SeedColumnTypesMatchManifestVsCatalog,
    SeedColumnsHaveDescriptions,
    SeedColumnsHaveTypes,
    SeedsHaveColumns,
    SeedsHaveDataTests,
    SeedsHaveDescriptions,
    SeedsHaveTags,
    SnapshotColumnsHaveDescriptions,
    SnapshotColumnsHaveTypes,
    SnapshotNamesMatchPattern,
    SnapshotsHaveColumns,
    SnapshotsHaveDataTests,
    SnapshotsHaveDescriptions,
    SnapshotsHaveTags,
    SourceColumnNamesMatchManifestVsCatalog,
    SourceColumnTypesMatchManifestVsCatalog,
    SourceColumnsHaveDescriptions,
    SourceColumnsHaveTypes,
    SourcesHaveColumns,
    SourcesHaveDataTests,
    SourcesHaveDescriptions,
    SourcesHaveFreshness,
    SourcesHaveLoader,
    SourcesHaveTags,
)
ALL_CHECKS_MAP = {check.check_name: check for check in ALL_CHECKS}
