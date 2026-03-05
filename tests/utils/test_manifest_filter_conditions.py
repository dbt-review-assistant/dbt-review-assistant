import pytest
from pathlib import Path

from utils.console_formatting import colour_message, ConsoleEmphasis
from utils.manifest_filter_conditions import ManifestFilterConditions


@pytest.mark.parametrize(
    ids=["base case", "Empty/None"],
    argnames=["kwargs", "expected_attributes"],
    argvalues=[
        (
            {
                "_include_materializations": ("table", "view"),
                "_include_packages": ["test_dbt_project", "another_dbt_project"],
                "_include_tags": {"test_tag", "another_tag"},
                "_include_paths": {
                    Path("test/model/path"),
                    Path("test/another/path"),
                },
                "_exclude_materializations": ("ephemeral", "incremental"),
                "_exclude_packages": ["one_more_dbt_project"],
                "_exclude_tags": {"one_more_tag"},
                "_exclude_paths": {Path("test/one/more/path")},
            },
            {
                "include_materializations": {"table", "view"},
                "include_packages": {"test_dbt_project", "another_dbt_project"},
                "include_tags": {"test_tag", "another_tag"},
                "include_paths": {
                    Path("test/model/path"),
                    Path("test/another/path"),
                },
                "exclude_materializations": {"ephemeral", "incremental"},
                "exclude_packages": {"one_more_dbt_project"},
                "exclude_tags": {"one_more_tag"},
                "exclude_paths": {Path("test/one/more/path")},
            },
        ),
        (
            {
                "_include_materializations": (),
                "_include_packages": None,
                "_include_tags": None,
                "_include_paths": None,
                "_exclude_materializations": [],
                "_exclude_packages": set(),
                "_exclude_tags": None,
                "_exclude_paths": None,
            },
            {
                "include_materializations": None,
                "include_packages": None,
                "include_tags": None,
                "include_paths": None,
                "exclude_materializations": None,
                "exclude_packages": None,
                "exclude_tags": None,
                "exclude_paths": None,
            },
        ),
    ],
)
def test_manifest_filter_conditions_post_init(kwargs, expected_attributes):
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
                "_include_materializations": ("table", "view"),
                "_include_packages": ["test_dbt_project", "another_dbt_project"],
                "_include_tags": {"test_tag", "another_tag"},
                "_include_paths": {
                    Path("test/model/path"),
                    Path("test/another/path"),
                },
                "_exclude_materializations": ("ephemeral", "incremental"),
                "_exclude_packages": ["one_more_dbt_project"],
                "_exclude_tags": {"one_more_tag"},
                "_exclude_paths": {Path("test/one/more/path")},
            },
            colour_message(
                """Including:
	materialized: table, view
	tags: another_tag, test_tag
	packages: another_dbt_project, test_dbt_project
	paths: test/another/path, test/model/path
Excluding:
	materialized: ephemeral, incremental
	tags: one_more_tag
	packages: one_more_dbt_project
	paths: test/one/more/path""",
                emphasis=ConsoleEmphasis.ITALIC,
            ),
        ),
        (
            {
                "_include_materializations": (),
                "_include_packages": None,
                "_include_tags": None,
                "_include_paths": None,
                "_exclude_materializations": [],
                "_exclude_packages": set(),
                "_exclude_tags": None,
                "_exclude_paths": None,
            },
            colour_message("", emphasis=ConsoleEmphasis.ITALIC),
        ),
    ],
)
def test_manifest_filter_conditions_summary(kwargs, expected_summary):
    assert ManifestFilterConditions(**kwargs).summary == expected_summary

