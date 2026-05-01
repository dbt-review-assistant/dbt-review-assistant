from argparse import Namespace
from contextlib import nullcontext as does_not_raise
from pathlib import Path
from typing import Optional, Type
from unittest.mock import Mock, patch

import pytest
from _pytest.raises import RaisesExc

from utils.artifact_data import Manifest
from utils.console_formatting import ConsoleEmphasis, colour_message
from utils.manifest_filter_conditions import (
    DirectChildrenFilterMethod,
    DirectParentsFilterMethod,
    IndirectChildrenFilterMethod,
    IndirectParentsFilterMethod,
    ManifestFilterConditions,
    ManifestFilterMethod,
    MaterializationFilterMethod,
    NamePatternFilterMethod,
    PackageFilterMethod,
    PathFilterMethod,
    ResourceTypeFilterMethod,
    TagFilterMethod,
    UniqueIdFilterMethod,
    try_filter_method,
)
from utils.manifest_object.manifest_object import (
    HasPatchPathMixin,
    ManifestColumn,
    ManifestObject,
)
from utils.manifest_object.node.model.model import ManifestModel


class ConcreteManifestObject(ManifestObject, HasPatchPathMixin):
    pass


@pytest.mark.parametrize(
    ids=[
        "Included model",
        "Included column",
        "Excluded model",
        "Excluded column",
    ],
    argnames=["filter_method", "manifest_object", "manifest", "expected_return"],
    argvalues=[
        (
            PathFilterMethod(Namespace(include_node_paths=[Path("test")])),
            ManifestModel({"original_file_path": "test"}),
            Mock(),
            True,
        ),
        (
            PathFilterMethod(Namespace(include_node_paths=[Path("test")])),
            ManifestColumn(
                {"name": "column_1"},
                parent=ManifestModel({"original_file_path": "test"}),
            ),
            Mock(),
            True,
        ),
        (
            PathFilterMethod(Namespace(exclude_node_paths=[Path("test")])),
            ManifestModel({"unique_id": "test_model", "original_file_path": "test"}),
            Mock(),
            False,
        ),
        (
            PathFilterMethod(Namespace(exclude_node_paths=[Path("test")])),
            ManifestColumn(
                {"name": "column_1"},
                parent=ManifestModel({"original_file_path": "test"}),
            ),
            Mock(),
            False,
        ),
    ],
)
def test_try_filter_method(
    filter_method: ManifestFilterMethod,
    manifest_object: ManifestObject,
    manifest: Manifest,
    expected_return: bool,
):
    assert (
        try_filter_method(filter_method, manifest_object, manifest) is expected_return
    )


@pytest.mark.parametrize(
    ids=["base case", "Empty/None", "Missing"],
    argnames=["kwargs", "expected_filters"],
    argvalues=[
        (
            {
                "include_materializations": ("table", "view"),
                "include_packages": ["test_dbt_project", "another_dbt_project"],
                "include_tags": {"test_tag", "another_tag"},
                "include_paths": {
                    Path("test/model/path"),
                    Path("test/another/path"),
                },
                "include_name_patterns": ["test_model", "another_model"],
                "include_resource_types": ["model"],
                "include_direct_parents": ["test_model"],
                "include_indirect_parents": ["another_model"],
                "include_direct_children": ["test_model"],
                "include_indirect_children": ["another_model"],
                "include_unique_ids": ["test_model"],
                "exclude_materializations": ("ephemeral", "incremental"),
                "exclude_packages": ["one_more_dbt_project"],
                "exclude_tags": {"one_more_tag"},
                "exclude_paths": {Path("test/one/more/path")},
                "exclude_name_patterns": ["excluded_model", "another_excluded_model"],
                "exclude_resource_types": ["source"],
                "exclude_direct_parents": ["one_more_model"],
                "exclude_indirect_parents": ["yet_another_model"],
                "exclude_direct_children": ["one_more_model"],
                "exclude_indirect_children": ["yet_another_model"],
                "exclude_unique_ids": ["another_model"],
            },
            (
                MaterializationFilterMethod(
                    Namespace(
                        include_materializations=("table", "view"),
                        exclude_materializations=("ephemeral", "incremental"),
                    ),
                ),
                PathFilterMethod(
                    Namespace(
                        include_paths={
                            Path("test/model/path"),
                            Path("test/another/path"),
                        },
                        exclude_materializations={Path("test/one/more/path")},
                    ),
                ),
                PackageFilterMethod(
                    Namespace(
                        include_packages={"test_dbt_project", "another_dbt_project"},
                        exclude_packages={"one_more_dbt_project"},
                    ),
                ),
                NamePatternFilterMethod(
                    Namespace(
                        include_name_patterns={"test_model", "another_model"},
                        exclude_name_patterns={
                            "excluded_model",
                            "another_excluded_model",
                        },
                    ),
                ),
                ResourceTypeFilterMethod(
                    Namespace(
                        include_resource_types={"model"},
                        exclude_resource_types={"source"},
                    ),
                ),
                TagFilterMethod(
                    Namespace(
                        include_tags={"test_tag", "another_tag"},
                        exclude_tags={"one_more_tag"},
                    ),
                ),
                DirectParentsFilterMethod(
                    Namespace(
                        include_direct_parents={"test_model"},
                        exclude_direct_parents={"one_more_model"},
                    )
                ),
                IndirectParentsFilterMethod(
                    Namespace(
                        include_indirect_parents={"another_model"},
                        exclude_indirect_parents={"yet_another_model"},
                    )
                ),
                DirectChildrenFilterMethod(
                    Namespace(
                        include_direct_children={"test_model"},
                        exclude_direct_children={"one_more_model"},
                    )
                ),
                IndirectChildrenFilterMethod(
                    Namespace(
                        include_indirect_children={"another_model"},
                        exclude_indirect_children={"yet_another_model"},
                    )
                ),
                UniqueIdFilterMethod(
                    Namespace(
                        include_unique_ids={"test_model"},
                        exclude_unique_ids={"another_model"},
                    )
                ),
            ),
        ),
        (
            {
                "include_materializations": None,
                "include_packages": None,
                "include_tags": None,
                "include_paths": None,
                "include_resource_types": None,
                "include_direct_parents": None,
                "include_indirect_parents": None,
                "include_direct_children": None,
                "include_indirect_children": None,
                "include_unique_ids": None,
                "exclude_materializations": None,
                "exclude_packages": None,
                "exclude_tags": None,
                "exclude_paths": None,
                "exclude_resource_types": None,
                "exclude_direct_parents": None,
                "exclude_indirect_parents": None,
                "exclude_direct_children": None,
                "exclude_indirect_children": None,
                "exclude_unique_ids": None,
            },
            (
                MaterializationFilterMethod(
                    Namespace(
                        include_materializations=None,
                        exclude_materializations=None,
                    ),
                ),
                PathFilterMethod(
                    Namespace(
                        include_paths=None,
                        exclude_materializations=None,
                    ),
                ),
                PackageFilterMethod(
                    Namespace(
                        include_packages=None,
                        exclude_packages=None,
                    ),
                ),
                NamePatternFilterMethod(
                    Namespace(
                        include_name_patterns=None,
                        exclude_name_patterns=None,
                    ),
                ),
                ResourceTypeFilterMethod(
                    Namespace(
                        include_resource_types=None,
                        exclude_resource_types=None,
                    ),
                ),
                TagFilterMethod(
                    Namespace(
                        include_tags=None,
                        exclude_tags=None,
                    ),
                ),
                DirectParentsFilterMethod(
                    Namespace(
                        include_direct_parents=None,
                        exclude_direct_parents=None,
                    )
                ),
                IndirectParentsFilterMethod(
                    Namespace(
                        include_indirect_parents=None,
                        exclude_indirect_parents=None,
                    )
                ),
                DirectChildrenFilterMethod(
                    Namespace(
                        include_direct_children=None,
                        exclude_direct_children=None,
                    )
                ),
                IndirectChildrenFilterMethod(
                    Namespace(
                        include_indirect_children=None,
                        exclude_indirect_children=None,
                    )
                ),
                UniqueIdFilterMethod(
                    Namespace(
                        include_unique_id=None,
                        exclude_unique_id=None,
                    )
                ),
            ),
        ),
        (
            {},
            (
                MaterializationFilterMethod(
                    Namespace(
                        include_materializations=None,
                        exclude_materializations=None,
                    ),
                ),
                PathFilterMethod(
                    Namespace(
                        include_paths=None,
                        exclude_materializations=None,
                    ),
                ),
                PackageFilterMethod(
                    Namespace(
                        include_packages=None,
                        exclude_packages=None,
                    ),
                ),
                NamePatternFilterMethod(
                    Namespace(
                        include_name_patterns=None,
                        exclude_name_patterns=None,
                    ),
                ),
                ResourceTypeFilterMethod(
                    Namespace(
                        include_resource_types=None,
                        exclude_resource_types=None,
                    ),
                ),
                TagFilterMethod(
                    Namespace(
                        include_tags=None,
                        exclude_tags=None,
                    ),
                ),
                DirectParentsFilterMethod(
                    Namespace(
                        include_direct_parents=None,
                        exclude_direct_parents=None,
                    )
                ),
                IndirectParentsFilterMethod(
                    Namespace(
                        include_indirect_parents=None,
                        exclude_indirect_parents=None,
                    )
                ),
                DirectChildrenFilterMethod(
                    Namespace(
                        include_direct_children=None,
                        exclude_direct_children=None,
                    )
                ),
                IndirectChildrenFilterMethod(
                    Namespace(
                        include_indirect_children=None,
                        exclude_indirect_children=None,
                    )
                ),
                UniqueIdFilterMethod(
                    Namespace(
                        include_unique_id={"test_model"},
                        exclude_unique_id={"another_model"},
                    )
                ),
            ),
        ),
    ],
)
def test_manifest_filter_conditions_post_init(kwargs, expected_filters):
    instance = ManifestFilterConditions(args=Namespace(**kwargs))
    assert instance.filter_methods == expected_filters


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
                "include_resource_types": {
                    "model",
                    "seed",
                },
                "include_name_patterns": {"test_model"},
                "exclude_materializations": ("ephemeral", "incremental"),
                "exclude_packages": ["one_more_dbt_project"],
                "exclude_tags": {"one_more_tag"},
                "exclude_node_paths": {Path("test/one/more/path")},
                "exclude_resource_types": {"snapshot"},
                "exclude_name_patterns": {"another_model"},
            },
            colour_message(
                """
Including:
	materializations: table, view
	paths: test/another/path, test/model/path
	packages: another_dbt_project, test_dbt_project
	name patterns: test_model
	resource types: model, seed
	tags: another_tag, test_tag
Excluding:
	materializations: ephemeral, incremental
	paths: test/one/more/path
	packages: one_more_dbt_project
	name patterns: another_model
	resource types: snapshot
	tags: one_more_tag""",
                emphasis=ConsoleEmphasis.ITALIC,
            ),
        ),
        (
            {
                "_include_materializations": (),
                "_include_packages": None,
                "_include_tags": None,
                "_include_paths": None,
                "_include_resource_types": None,
                "_include_name_patterns": None,
                "_exclude_materializations": [],
                "_exclude_packages": set(),
                "_exclude_tags": None,
                "_exclude_paths": None,
                "_exclude_resource_types": None,
                "_exclude_name_patterns": None,
            },
            colour_message("", emphasis=ConsoleEmphasis.ITALIC),
        ),
    ],
)
def test_manifest_filter_conditions_summary(kwargs, expected_summary):
    assert ManifestFilterConditions(Namespace(**kwargs)).summary == expected_summary


@pytest.mark.parametrize(
    argnames=[
        "data",
        "include_name_patterns",
        "exclude_name_patterns",
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
                "name": "included_model",
            },
            ["included_[a-z]*", "another_model"],
            None,
            True,
        ),
        (
            {
                "name": "excluded_model",
            },
            ["included_[a-z]*"],
            None,
            False,
        ),
        (
            {
                "name": "excluded_model",
            },
            None,
            ["excluded_[a-z]*", "another_model"],
            False,
        ),
        (
            {
                "name": "included_model",
            },
            None,
            ["excluded_[a-z]*"],
            True,
        ),
        (
            {
                "name": "included_model",
            },
            ["included_[a-z]*"],
            ["excluded_[a-z]*"],
            True,
        ),
        (
            {
                "name": "excluded_model",
            },
            ["included_[a-z]*"],
            ["excluded_[a-z]*"],
            False,
        ),
        (
            {
                "name": "excluded_model",
            },
            ["excluded_[a-z]*"],
            ["excluded_[a-z]*"],
            False,
        ),
    ],
)
def test_name_pattern_filter_method_is_manifest_object_in_scope(
    data: dict,
    include_name_patterns: list[str],
    exclude_name_patterns: list[str],
    expected_return: bool,
):
    manifest_object = ConcreteManifestObject(data)
    instance = NamePatternFilterMethod(
        args=Namespace(
            include_name_patterns=include_name_patterns,
            exclude_name_patterns=exclude_name_patterns,
        )
    )
    assert instance.is_manifest_object_in_scope(manifest_object) is expected_return


@pytest.mark.parametrize(
    argnames=[
        "data",
        "include_unique_ids",
        "exclude_unique_ids",
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
                "unique_id": "included_model",
            },
            ["included_model", "another_model"],
            None,
            True,
        ),
        (
            {
                "unique_id": "excluded_model",
            },
            ["included_model"],
            None,
            False,
        ),
        (
            {
                "unique_id": "excluded_model",
            },
            None,
            ["excluded_model", "another_model"],
            False,
        ),
        (
            {
                "unique_id": "included_model",
            },
            None,
            ["excluded_model"],
            True,
        ),
        (
            {
                "unique_id": "included_model",
            },
            ["included_model"],
            ["excluded_model"],
            True,
        ),
        (
            {
                "unique_id": "excluded_model",
            },
            ["included_model"],
            ["excluded_model"],
            False,
        ),
        (
            {
                "unique_id": "excluded_model",
            },
            ["excluded_model"],
            ["excluded_model"],
            False,
        ),
    ],
)
def test_unique_id_filter_method_is_manifest_object_in_scope(
    data: dict,
    include_unique_ids: list[str],
    exclude_unique_ids: list[str],
    expected_return: bool,
):
    manifest_object = ConcreteManifestObject(data)
    instance = UniqueIdFilterMethod(
        args=Namespace(
            include_unique_ids=include_unique_ids,
            exclude_unique_ids=exclude_unique_ids,
        )
    )
    assert instance.is_manifest_object_in_scope(manifest_object) is expected_return


@pytest.mark.parametrize(
    argnames=[
        "data",
        "include_name_patterns",
        "exclude_name_patterns",
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
                "name": "included_model",
            },
            ["included_[a-z]*", "another_model"],
            None,
            True,
        ),
        (
            {
                "name": "excluded_model",
            },
            ["included_[a-z]*"],
            None,
            False,
        ),
        (
            {
                "name": "excluded_model",
            },
            None,
            ["excluded_[a-z]*", "another_model"],
            False,
        ),
        (
            {
                "name": "included_model",
            },
            None,
            ["excluded_[a-z]*"],
            True,
        ),
        (
            {
                "name": "included_model",
            },
            ["included_[a-z]*"],
            ["excluded_[a-z]*"],
            True,
        ),
        (
            {
                "name": "excluded_model",
            },
            ["included_[a-z]*"],
            ["excluded_[a-z]*"],
            False,
        ),
        (
            {
                "name": "excluded_model",
            },
            ["excluded_[a-z]*"],
            ["excluded_[a-z]*"],
            False,
        ),
    ],
)
def test_manifest_object_filter_method_post_init(
    data: dict,
    include_name_patterns: list[str],
    exclude_name_patterns: list[str],
    expected_return: bool,
):
    manifest_object = ConcreteManifestObject(data)
    instance = NamePatternFilterMethod(
        args=Namespace(
            include_name_patterns=include_name_patterns,
            exclude_name_patterns=exclude_name_patterns,
        )
    )
    assert instance.is_manifest_object_in_scope(manifest_object) is expected_return


@pytest.mark.parametrize(
    argnames=[
        "data",
        "include_packages",
        "exclude_packages",
        "expected_return",
        "expected_raise",
    ],
    ids=[
        "Explicitly included",
        "Not explicitly included",
        "Explicitly excluded",
        "Not explicitly excluded",
        "Explicitly included, with exclude condition",
        "Explicitly excluded, with include condition",
        "Both explicitly included and explicitly excluded - exclude should take precedence",
        "Package is None",
    ],
    argvalues=[
        (
            {
                "unique_id": "included-model",
                "package_name": "test_dbt_package",
            },
            ["test_dbt_package"],
            None,
            True,
            does_not_raise(),
        ),
        (
            {
                "unique_id": "excluded-model",
                "package_name": "another_dbt_package",
            },
            ["test_dbt_package"],
            None,
            False,
            does_not_raise(),
        ),
        (
            {
                "unique_id": "excluded-model",
                "package_name": "test_dbt_package",
            },
            None,
            ["test_dbt_package"],
            False,
            does_not_raise(),
        ),
        (
            {
                "unique_id": "excluded-model",
                "package_name": "another_dbt_package",
            },
            None,
            ["test_dbt_package"],
            True,
            does_not_raise(),
        ),
        (
            {
                "unique_id": "included-model",
                "package_name": "test_dbt_package",
            },
            ["test_dbt_package"],
            ["different_dbt_package"],
            True,
            does_not_raise(),
        ),
        (
            {
                "unique_id": "excluded-model",
                "package_name": "test_dbt_package",
            },
            ["different_dbt_package"],
            ["test_dbt_package"],
            False,
            does_not_raise(),
        ),
        (
            {
                "unique_id": "excluded-model",
                "package_name": "test_dbt_package",
            },
            ["test_dbt_package"],
            ["test_dbt_package"],
            False,
            does_not_raise(),
        ),
        (
            {
                "unique_id": "excluded-model",
            },
            ["test_dbt_package"],
            ["test_dbt_package"],
            False,
            pytest.raises(NotImplementedError),
        ),
    ],
)
def test_package_filter_method_is_manifest_object_in_scope(
    data: dict,
    include_packages: list[str],
    exclude_packages: list[str],
    expected_return: bool,
    expected_raise: does_not_raise | RaisesExc[BaseException],
):
    manifest_object = ConcreteManifestObject(data)
    instance = PackageFilterMethod(
        args=Namespace(
            include_packages=include_packages,
            exclude_packages=exclude_packages,
        )
    )
    with expected_raise:
        assert instance.is_manifest_object_in_scope(manifest_object) is expected_return


@pytest.mark.parametrize(
    argnames=[
        "data",
        "include_paths",
        "exclude_paths",
        "expected_return",
        "expected_raise",
    ],
    ids=[
        "Explicitly included",
        "Not explicitly included",
        "Explicitly excluded",
        "Not explicitly excluded",
        "Explicitly included, with exclude condition",
        "Explicitly excluded, with include condition",
        "Both explicitly included and explicitly excluded - exclude should take precedence",
        "Exact filepath match",
        "No original filepath",
    ],
    argvalues=[
        (
            {
                "unique_id": "included-model",
                "original_file_path": "test/model/path",
            },
            [Path("test/model/")],
            None,
            True,
            does_not_raise(),
        ),
        (
            {
                "unique_id": "excluded-model",
                "original_file_path": "test/model/path",
            },
            [Path("test/model/subdir/")],
            None,
            False,
            does_not_raise(),
        ),
        (
            {
                "unique_id": "excluded-model",
                "original_file_path": "test/model/path",
            },
            None,
            [Path("test/model/")],
            False,
            does_not_raise(),
        ),
        (
            {
                "unique_id": "included-model",
                "original_file_path": "test/model/path",
            },
            None,
            [Path("test/model/subdir/")],
            True,
            does_not_raise(),
        ),
        (
            {
                "unique_id": "included-model",
                "original_file_path": "test/model/path",
            },
            [Path("test/model/")],
            [Path("test/model/subdir/")],
            True,
            does_not_raise(),
        ),
        (
            {
                "unique_id": "excluded-model",
                "original_file_path": "test/model/path",
            },
            [Path("test/model/subdir/")],
            [Path("test/model/")],
            False,
            does_not_raise(),
        ),
        (
            {
                "unique_id": "excluded-model",
                "original_file_path": "test/model/path",
            },
            [Path("test/model/")],
            [Path("test/model")],
            False,
            does_not_raise(),
        ),
        (
            {
                "unique_id": "included-model",
                "original_file_path": "test/model/path.sql",
            },
            [Path("test/model/path.sql")],
            None,
            True,
            does_not_raise(),
        ),
        (
            {
                "unique_id": "included-model",
            },
            [Path("test/model/")],
            None,
            True,
            pytest.raises(NotImplementedError),
        ),
    ],
)
def test_path_filter_method_is_manifest_object_in_scope(
    data: dict,
    include_paths: list[Path],
    exclude_paths: list[Path],
    expected_return: bool,
    expected_raise: does_not_raise | RaisesExc[BaseException],
):
    manifest_object = ConcreteManifestObject(data)
    instance = PathFilterMethod(
        args=Namespace(
            include_node_paths=include_paths,
            exclude_node_paths=exclude_paths,
        )
    )
    with expected_raise:
        assert instance.is_manifest_object_in_scope(manifest_object) is expected_return


@pytest.mark.parametrize(
    argnames=[
        "data",
        "include_resource_types",
        "exclude_resource_types",
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
            },
            ["model"],
            None,
            True,
        ),
        (
            {
                "unique_id": "excluded-model",
                "resource_type": "model",
            },
            ["seed"],
            None,
            False,
        ),
        (
            {
                "unique_id": "excluded-model",
                "resource_type": "model",
            },
            None,
            ["model"],
            False,
        ),
        (
            {
                "unique_id": "included-model",
                "resource_type": "model",
            },
            None,
            ["seed"],
            True,
        ),
        (
            {
                "unique_id": "included-model",
                "resource_type": "model",
            },
            ["model"],
            ["seed"],
            True,
        ),
        (
            {
                "unique_id": "excluded-model",
                "resource_type": "model",
            },
            ["seed"],
            ["model"],
            False,
        ),
        (
            {
                "unique_id": "excluded-model",
                "resource_type": "model",
            },
            ["model"],
            ["model"],
            False,
        ),
    ],
)
def test_resource_type_filter_method_is_manifest_object_in_scope(
    data: dict,
    include_resource_types: list[str],
    exclude_resource_types: list[str],
    expected_return: bool,
):
    manifest_object = ConcreteManifestObject(data)
    instance = ResourceTypeFilterMethod(
        args=Namespace(
            include_resource_types=include_resource_types,
            exclude_resource_types=exclude_resource_types,
        )
    )
    assert instance.is_manifest_object_in_scope(manifest_object) is expected_return


@pytest.mark.parametrize(
    argnames=[
        "data",
        "object_type",
        "include_materializations",
        "exclude_materializations",
        "expected_return",
        "expected_raise",
    ],
    ids=[
        "Explicitly included",
        "Not explicitly included",
        "Explicitly excluded",
        "Not explicitly excluded",
        "Explicitly included, with exclude condition",
        "Explicitly excluded, with include condition",
        "Both explicitly included and explicitly excluded - exclude should take precedence",
        "Not a model",
    ],
    argvalues=[
        (
            {
                "unique_id": "included-model",
                "resource_type": "model",
                "config": {"materialized": "view"},
            },
            ManifestModel,
            ["view"],
            None,
            True,
            does_not_raise(),
        ),
        (
            {
                "unique_id": "included-model",
                "resource_type": "model",
                "config": {"materialized": "view"},
            },
            ManifestModel,
            ["table"],
            None,
            False,
            does_not_raise(),
        ),
        (
            {
                "unique_id": "included-model",
                "resource_type": "model",
                "config": {"materialized": "view"},
            },
            ManifestModel,
            None,
            ["view"],
            False,
            does_not_raise(),
        ),
        (
            {
                "unique_id": "included-model",
                "resource_type": "model",
                "config": {"materialized": "view"},
            },
            ManifestModel,
            None,
            ["table"],
            True,
            does_not_raise(),
        ),
        (
            {
                "unique_id": "included-model",
                "resource_type": "model",
                "config": {"materialized": "view"},
            },
            ManifestModel,
            ["view"],
            ["table"],
            True,
            does_not_raise(),
        ),
        (
            {
                "unique_id": "included-model",
                "resource_type": "model",
                "config": {"materialized": "table"},
            },
            ManifestModel,
            ["view"],
            ["table"],
            False,
            does_not_raise(),
        ),
        (
            {
                "unique_id": "included-model",
                "resource_type": "model",
                "config": {"materialized": "view"},
            },
            ManifestModel,
            ["view"],
            ["view"],
            False,
            does_not_raise(),
        ),
        (
            {
                "unique_id": "included-model",
                "resource_type": "model",
                "config": {"materialized": "view"},
            },
            ManifestObject,
            ["view"],
            None,
            True,
            pytest.raises(NotImplementedError),
        ),
    ],
)
def test_manifest_object_filter_nodes_by_materialization_type(
    data: dict,
    object_type: Type[ManifestObject],
    include_materializations: list[str],
    exclude_materializations: list[str],
    expected_return: bool,
    expected_raise: does_not_raise | RaisesExc[BaseException],
):
    manifest_object = object_type(data)
    instance = MaterializationFilterMethod(
        args=Namespace(
            include_materializations=include_materializations,
            exclude_materializations=exclude_materializations,
        )
    )
    with expected_raise:
        assert instance.is_manifest_object_in_scope(manifest_object) is expected_return


@pytest.mark.parametrize(
    argnames=[
        "data",
        "object_type",
        "include_tags",
        "exclude_tags",
        "expected_return",
        "expected_raise",
    ],
    ids=[
        "Explicitly included",
        "Not explicitly included",
        "Explicitly excluded",
        "Not explicitly excluded",
        "Explicitly included, with exclude condition",
        "Explicitly excluded, with include condition",
        "Both explicitly included and explicitly excluded - exclude should take precedence",
        "Not a model",
    ],
    argvalues=[
        (
            {
                "unique_id": "included-model",
                "tags": ["test_tag", "another_tag"],
            },
            ManifestModel,
            ["test_tag"],
            None,
            True,
            does_not_raise(),
        ),
        (
            {
                "unique_id": "excluded-model",
                "tags": ["test_tag", "another_tag"],
            },
            ManifestModel,
            ["different_tag"],
            None,
            False,
            does_not_raise(),
        ),
        (
            {
                "unique_id": "excluded-model",
                "tags": ["test_tag", "another_tag"],
            },
            ManifestModel,
            None,
            ["test_tag"],
            False,
            does_not_raise(),
        ),
        (
            {
                "unique_id": "included-model",
                "tags": ["test_tag", "another_tag"],
            },
            ManifestModel,
            None,
            ["different_tag"],
            True,
            does_not_raise(),
        ),
        (
            {
                "unique_id": "included-model",
                "tags": ["test_tag", "another_tag"],
            },
            ManifestModel,
            ["test_tag"],
            ["different_tag"],
            True,
            does_not_raise(),
        ),
        (
            {
                "unique_id": "excluded-model",
                "tags": ["test_tag", "another_tag"],
            },
            ManifestModel,
            ["different_tag"],
            ["another_tag"],
            False,
            does_not_raise(),
        ),
        (
            {
                "unique_id": "excluded-model",
                "tags": ["test_tag", "another_tag"],
            },
            ManifestModel,
            ["test_tag"],
            ["another_tag"],
            False,
            does_not_raise(),
        ),
        (
            {
                "unique_id": "included-model",
                "tags": ["test_tag", "another_tag"],
            },
            ManifestObject,
            ["test_tag"],
            None,
            True,
            pytest.raises(NotImplementedError),
        ),
    ],
)
def test_tag_filter_method_is_manifest_object_in_scope(
    data: dict,
    object_type: Type[ManifestObject],
    include_tags: list[str],
    exclude_tags: list[str],
    expected_return: bool,
    expected_raise: does_not_raise | RaisesExc[BaseException],
):
    manifest_object = object_type(data)
    instance = TagFilterMethod(
        args=Namespace(
            include_tags=include_tags,
            exclude_tags=exclude_tags,
        )
    )
    with expected_raise:
        assert instance.is_manifest_object_in_scope(manifest_object) is expected_return


@pytest.mark.parametrize(
    argnames=[
        "data",
        "include_direct_parents",
        "direct_parents",
        "manifest",
        "expected_return",
        "expected_raise",
    ],
    ids=[
        "Explicitly included",
        "Not explicitly included",
        "Manifest None",
        "Parent map is None",
    ],
    argvalues=[
        (
            {
                "unique_id": "included_model",
            },
            ["test_model", "another_model"],
            {"test_model"},
            Mock(),
            True,
            does_not_raise(),
        ),
        (
            {
                "unique_id": "excluded_model",
            },
            ["test_model", "another_model"],
            {"one_more_model"},
            Mock(),
            False,
            does_not_raise(),
        ),
        (
            {
                "unique_id": "included_model",
            },
            ["test_model", "another_model"],
            {"test_model"},
            None,
            True,
            pytest.raises(ValueError, match="cannot be None"),
        ),
        (
            {
                "unique_id": "included_model",
            },
            ["test_model", "another_model"],
            {"test_model"},
            Mock(parent_map={}),
            True,
            pytest.raises(NotImplementedError),
        ),
    ],
)
def test_direct_parents_filter_method_is_manifest_object_included(
    data: dict,
    include_direct_parents: list[str],
    direct_parents: set[str],
    manifest: None | Mock,
    expected_return: bool,
    expected_raise: does_not_raise | RaisesExc[BaseException],
):
    manifest_object = ConcreteManifestObject(data)
    with patch(
        "utils.manifest_filter_conditions.get_direct_parents",
        return_value=direct_parents,
    ):
        instance = DirectParentsFilterMethod(
            args=Namespace(
                include_direct_parents=include_direct_parents,
            ),
        )
        with expected_raise:
            assert (
                instance.is_manifest_object_in_scope(manifest_object, manifest=manifest)
                is expected_return
            )


@pytest.mark.parametrize(
    argnames=[
        "data",
        "include_indirect_parents",
        "indirect_parents",
        "manifest",
        "expected_return",
        "expected_raise",
    ],
    ids=[
        "Explicitly included",
        "Not explicitly included",
        "Manifest None",
        "Parent map is None",
    ],
    argvalues=[
        (
            {
                "unique_id": "included_model",
            },
            ["test_model", "another_model"],
            {"test_model"},
            Mock(),
            True,
            does_not_raise(),
        ),
        (
            {
                "unique_id": "excluded_model",
            },
            ["test_model", "another_model"],
            {"one_more_model"},
            Mock(),
            False,
            does_not_raise(),
        ),
        (
            {
                "unique_id": "included_model",
            },
            ["test_model", "another_model"],
            {"test_model"},
            None,
            True,
            pytest.raises(ValueError, match="cannot be None"),
        ),
        (
            {
                "unique_id": "included_model",
            },
            ["test_model", "another_model"],
            {"test_model"},
            Mock(parent_map={}),
            True,
            pytest.raises(NotImplementedError),
        ),
    ],
)
def test_indirect_parents_filter_method_is_manifest_object_included(
    data: dict,
    include_indirect_parents: list[str],
    indirect_parents: set[str],
    manifest: None | Mock,
    expected_return: bool,
    expected_raise: does_not_raise | RaisesExc[BaseException],
):
    manifest_object = ConcreteManifestObject(data)
    with patch(
        "utils.manifest_filter_conditions.get_all_parents",
        return_value=indirect_parents,
    ):
        instance = IndirectParentsFilterMethod(
            args=Namespace(
                include_indirect_parents=include_indirect_parents,
            ),
        )
        with expected_raise:
            assert (
                instance.is_manifest_object_in_scope(manifest_object, manifest=manifest)
                is expected_return
            )


@pytest.mark.parametrize(
    argnames=[
        "data",
        "include_direct_children",
        "direct_children",
        "manifest",
        "expected_return",
        "expected_raise",
    ],
    ids=[
        "Explicitly included",
        "Not explicitly included",
        "Manifest None",
        "Child map is None",
    ],
    argvalues=[
        (
            {
                "unique_id": "included_model",
            },
            ["test_model", "another_model"],
            {"test_model"},
            Mock(),
            True,
            does_not_raise(),
        ),
        (
            {
                "unique_id": "excluded_model",
            },
            ["test_model", "another_model"],
            {"one_more_model"},
            Mock(),
            False,
            does_not_raise(),
        ),
        (
            {
                "unique_id": "included_model",
            },
            ["test_model", "another_model"],
            {"test_model"},
            None,
            True,
            pytest.raises(ValueError, match="cannot be None"),
        ),
        (
            {
                "unique_id": "included_model",
            },
            ["test_model", "another_model"],
            {"test_model"},
            Mock(child_map={}),
            True,
            pytest.raises(NotImplementedError),
        ),
    ],
)
def test_direct_children_filter_method_is_manifest_object_included(
    data: dict,
    include_direct_children: list[str],
    direct_children: set[str],
    manifest: None | Mock,
    expected_return: bool,
    expected_raise: does_not_raise | RaisesExc[BaseException],
):
    manifest_object = ConcreteManifestObject(data)
    with patch(
        "utils.manifest_filter_conditions.get_direct_children",
        return_value=direct_children,
    ):
        instance = DirectChildrenFilterMethod(
            args=Namespace(
                include_direct_children=include_direct_children,
            ),
        )
        with expected_raise:
            assert (
                instance.is_manifest_object_in_scope(manifest_object, manifest=manifest)
                is expected_return
            )


@pytest.mark.parametrize(
    argnames=[
        "data",
        "include_indirect_children",
        "indirect_children",
        "manifest",
        "expected_return",
        "expected_raise",
    ],
    ids=[
        "Explicitly included",
        "Not explicitly included",
        "Manifest None",
        "Child map is None",
    ],
    argvalues=[
        (
            {
                "unique_id": "included_model",
            },
            ["test_model", "another_model"],
            {"test_model"},
            Mock(),
            True,
            does_not_raise(),
        ),
        (
            {
                "unique_id": "excluded_model",
            },
            ["test_model", "another_model"],
            {"one_more_model"},
            Mock(),
            False,
            does_not_raise(),
        ),
        (
            {
                "unique_id": "included_model",
            },
            ["test_model", "another_model"],
            {"test_model"},
            None,
            True,
            pytest.raises(ValueError, match="cannot be None"),
        ),
        (
            {
                "unique_id": "included_model",
            },
            ["test_model", "another_model"],
            {"test_model"},
            Mock(child_map={}),
            True,
            pytest.raises(NotImplementedError),
        ),
    ],
)
def test_indirect_children_filter_method_is_manifest_object_included(
    data: dict,
    include_indirect_children: list[str],
    indirect_children: set[str],
    manifest: None | Mock,
    expected_return: bool,
    expected_raise: does_not_raise | RaisesExc[BaseException],
):
    manifest_object = ConcreteManifestObject(data)
    with patch(
        "utils.manifest_filter_conditions.get_all_children",
        return_value=indirect_children,
    ):
        instance = IndirectChildrenFilterMethod(
            args=Namespace(
                include_indirect_children=include_indirect_children,
            ),
        )
        with expected_raise:
            assert (
                instance.is_manifest_object_in_scope(manifest_object, manifest=manifest)
                is expected_return
            )


@pytest.mark.parametrize(
    argnames=[
        "data",
        "args",
        "object_type",
        "manifest",
        "expected_return",
    ],
    ids=[
        "No filters",
        "All filters pass",
        "One filter fails",
        "One filter not implemented",
        "All filters fail",
        "Direct parent filter",
    ],
    argvalues=[
        (
            {"unique_id": "included_model"},
            Namespace(),
            ManifestModel,
            Mock(),
            True,
        ),
        (
            {
                "unique_id": "included-model",
                "resource_type": "model",
                "config": {"materialized": "view"},
            },
            Namespace(
                include_resource_types=["model"],
                include_materializations=["view"],
                exclude_resource_types=["source"],
            ),
            ManifestModel,
            Mock(),
            True,
        ),
        (
            {
                "unique_id": "included-model",
                "resource_type": "model",
                "config": {"materialized": "view"},
            },
            Namespace(
                include_resource_types=["model"],
                include_materializations=["table"],
                exclude_resource_types=["source"],
            ),
            ManifestModel,
            Mock(),
            False,
        ),
        (
            {
                "unique_id": "included-source",
                "resource_type": "source",
            },
            Namespace(
                include_materializations=["table"],
            ),
            ConcreteManifestObject,
            Mock(),
            True,
        ),
        (
            {
                "unique_id": "included-model",
                "resource_type": "model",
                "config": {"materialized": "view"},
            },
            Namespace(
                include_materializations=["view"],
                exclude_resource_types=["model"],
            ),
            ManifestModel,
            Mock(),
            False,
        ),
        (
            {
                "unique_id": "included-model",
                "resource_type": "model",
                "config": {"materialized": "view"},
            },
            Namespace(
                include_resource_types=["model"],
                include_materializations=["view"],
                exclude_resource_types=["source"],
            ),
            ManifestModel,
            Mock(),
            True,
        ),
    ],
)
def test_manifest_filter_conditions_is_manifest_object_in_scope(
    data: dict,
    args: Namespace,
    object_type: Type[ManifestObject],
    manifest: Mock,
    expected_return: bool,
):
    manifest_object = object_type(data)
    instance = ManifestFilterConditions(args)
    assert (
        instance.is_manifest_object_in_scope(manifest_object, manifest)
        is expected_return
    )


class ConcreteManifestFilterMethod(ManifestFilterMethod):
    @property
    def arg_name_suffix(self) -> str:
        return "test_filter"

    def is_manifest_object_in_scope(
        self, manifest_object: "ManifestObject", manifest: Optional["Manifest"] = None
    ) -> bool:
        return True


@pytest.mark.parametrize(
    ids=[
        "With values",
        "None",
    ],
    argnames=[
        "include_values",
        "exclude_values",
        "expected_include_values",
        "expected_exclude_values",
    ],
    argvalues=[
        (
            ["test", "test2"],
            ["test", "test2"],
            {"test", "test2"},
            {"test", "test2"},
        ),
        (None, None, None, None),
    ],
)
def test_manifest_filter_method_post_init(
    include_values: list[str] | None,
    exclude_values: list[str] | None,
    expected_include_values: set[str] | None,
    expected_exclude_values: set[str] | None,
):
    instance = ConcreteManifestFilterMethod(
        args=Namespace(
            include_test_filter=include_values,
            exclude_test_filter=exclude_values,
        )
    )
    assert instance.include_values == expected_include_values
    assert instance.exclude_values == expected_exclude_values


@pytest.mark.parametrize(
    ids=[
        "With include values",
        "With exclude values",
        "None",
        "Not a collection",
    ],
    argnames=[
        "include_values",
        "exclude_values",
        "prefix",
        "expected_return",
        "expected_raise",
    ],
    argvalues=[
        (
            ["test", "test2"],
            ["test3", "test4"],
            "include",
            {"test", "test2"},
            does_not_raise(),
        ),
        (
            ["test", "test2"],
            ["test3", "test4"],
            "exclude",
            {"test3", "test4"},
            does_not_raise(),
        ),
        (
            None,
            None,
            "include",
            None,
            does_not_raise(),
        ),
        (
            Mock("test"),
            ["test3", "test4"],
            "include",
            {"test", "test2"},
            pytest.raises(TypeError, match="is not a Collection"),
        ),
    ],
)
def test_manifest_filter_method_get_values_from_args(
    include_values: list[str] | None,
    exclude_values: list[str] | None,
    prefix: str,
    expected_return: set[str] | None,
    expected_raise: does_not_raise | RaisesExc[BaseException],
):
    instance = ConcreteManifestFilterMethod()
    with expected_raise:
        assert (
            instance.get_values_from_args(
                args=Namespace(
                    include_test_filter=include_values,
                    exclude_test_filter=exclude_values,
                ),
                prefix=prefix,
            )
            == expected_return
        )


@pytest.mark.parametrize(
    ids=[
        "With include values",
        "None",
    ],
    argnames=[
        "include_values",
        "expected_return",
    ],
    argvalues=[
        (
            ["test", "test2"],
            "test filter: test, test2",
        ),
        (None, ""),
    ],
)
def test_manifest_filter_method_includes_summary(
    include_values: list[str] | None,
    expected_return: set[str] | None,
):
    instance = ConcreteManifestFilterMethod(
        Namespace(include_test_filter=include_values)
    )
    assert instance.includes_summary == expected_return


@pytest.mark.parametrize(
    ids=[
        "With exclude values",
        "None",
    ],
    argnames=[
        "exclude_values",
        "expected_return",
    ],
    argvalues=[
        (
            ["test", "test2"],
            "test filter: test, test2",
        ),
        (None, ""),
    ],
)
def test_manifest_filter_method_excludes_summary(
    exclude_values: list[str] | None,
    expected_return: set[str] | None,
):
    instance = ConcreteManifestFilterMethod(
        Namespace(exclude_test_filter=exclude_values)
    )
    assert instance.excludes_summary == expected_return
