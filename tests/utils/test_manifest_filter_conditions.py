import pytest
from pathlib import Path
from utils.manifest_filter_conditions import ManifestFilterConditions


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
                include_paths=(Path("test/model/path"), Path("test/another/path")),
                exclude_materializations=("ephemeral", "incremental"),
                exclude_packages=("one_more_dbt_project",),
                exclude_tags=("one_more_tag",),
                exclude_paths=(Path("test/one/more/path"),),
            ),
            ManifestFilterConditions(
                include_materializations=("table", "view"),
                include_packages=("test_dbt_project", "another_dbt_project"),
                include_tags=("test_tag", "another_tag"),
                include_paths=(Path("test/model/path"), Path("test/another/path")),
                exclude_materializations=("ephemeral", "incremental"),
                exclude_packages=("one_more_dbt_project",),
                exclude_tags=("one_more_tag",),
                exclude_paths=(Path("test/one/more/path"),),
            ),
            True,
        ),
        (
            ManifestFilterConditions(
                include_materializations=("table", "view"),
                include_packages=("test_dbt_project", "another_dbt_project"),
                include_tags=("test_tag", "another_tag"),
                include_paths=(Path("test/model/path"), Path("test/another/path")),
                exclude_materializations=("ephemeral", "incremental"),
                exclude_packages=("one_more_dbt_project",),
                exclude_tags=("one_more_tag",),
                exclude_paths=(Path("test/one/more/path"),),
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
