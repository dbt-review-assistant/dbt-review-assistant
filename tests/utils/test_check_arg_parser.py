import argparse
import sys
from pathlib import Path
from unittest.mock import patch, call, ANY, _Call

import pytest

from utils.check_arg_parser import CheckArgParser, CliArgument


@pytest.mark.parametrize(
    argnames=["name", "expected_cli_arg_name"],
    ids=["One word", "Two words"],
    argvalues=[
        ("test", "--test"),
        ("test_two", "--test-two"),
    ],
)
def test_cli_argument_cli_name(name: str, expected_cli_arg_name: str):
    arg = CliArgument(
        name,
        help="",
        type=str,
    )
    assert arg.cli_name == expected_cli_arg_name


def test_dbt_pre_commit_hooks_argument_parser_post_init():
    with (
        patch.object(CheckArgParser, "add_arguments") as mock_add_arguments,
        patch("utils.check_arg_parser.argparse.ArgumentParser") as mock_parser,
    ):
        instance = CheckArgParser(
            "unit_test",
        )
        assert instance.parser is mock_parser()
        mock_add_arguments.assert_called_once()


@pytest.mark.parametrize(
    argnames=["additional_arguments", "expected_calls"],
    ids=["Universal arguments only", "Universal and optional arguments"],
    argvalues=[
        (
            [],
            [
                call(
                    "--project-dir",
                    type=Path,
                    help=ANY,
                    nargs=None,
                    required=False,
                    default=None,
                ),
                call(
                    "--manifest-dir",
                    type=Path,
                    help=ANY,
                    nargs=None,
                    required=False,
                    default=None,
                ),
                call(
                    "--catalog-dir",
                    type=Path,
                    help=ANY,
                    nargs=None,
                    required=False,
                    default=None,
                ),
            ],
        ),
        (
            [
                "must_have_all_constraints_from",
                "must_have_any_constraint_from",
                "must_have_all_data_tests_from",
                "must_have_any_data_test_from",
                "must_have_all_tags_from",
                "must_have_any_tag_from",
                "include_packages",
                "include_materializations",
                "include_tags",
                "exclude_packages",
                "exclude_materializations",
                "exclude_tags",
            ],
            [
                call(
                    "--project-dir",
                    type=Path,
                    help=ANY,
                    nargs=None,
                    required=False,
                    default=None,
                ),
                call(
                    "--manifest-dir",
                    type=Path,
                    help=ANY,
                    nargs=None,
                    required=False,
                    default=None,
                ),
                call(
                    "--catalog-dir",
                    type=Path,
                    help=ANY,
                    nargs=None,
                    required=False,
                    default=None,
                ),
                call(
                    "--must-have-all-constraints-from",
                    type=str,
                    help=ANY,
                    nargs="+",
                    required=False,
                    default=None,
                ),
                call(
                    "--must-have-any-constraint-from",
                    type=str,
                    help=ANY,
                    nargs="+",
                    required=False,
                    default=None,
                ),
                call(
                    "--must-have-all-data-tests-from",
                    type=str,
                    help=ANY,
                    nargs="+",
                    required=False,
                    default=None,
                ),
                call(
                    "--must-have-any-data-test-from",
                    type=str,
                    help=ANY,
                    nargs="+",
                    required=False,
                    default=None,
                ),
                call(
                    "--must-have-all-tags-from",
                    type=str,
                    help=ANY,
                    nargs="+",
                    required=False,
                    default=None,
                ),
                call(
                    "--must-have-any-tag-from",
                    type=str,
                    help=ANY,
                    nargs="+",
                    required=False,
                    default=None,
                ),
                call(
                    "--include-materializations",
                    type=str,
                    help=ANY,
                    nargs="+",
                    required=False,
                    default=None,
                ),
                call(
                    "--include-tags",
                    type=str,
                    help=ANY,
                    nargs="+",
                    required=False,
                    default=None,
                ),
                call(
                    "--include-packages",
                    type=str,
                    help=ANY,
                    nargs="+",
                    required=False,
                    default=None,
                ),
                call(
                    "--exclude-materializations",
                    type=str,
                    help=ANY,
                    nargs="+",
                    required=False,
                    default=None,
                ),
                call(
                    "--exclude-tags",
                    type=str,
                    help=ANY,
                    nargs="+",
                    required=False,
                    default=None,
                ),
                call(
                    "--exclude-packages",
                    type=str,
                    help=ANY,
                    nargs="+",
                    required=False,
                    default=None,
                ),
            ],
        ),
    ],
)
def test_dbt_pre_commit_hooks_argument_parser_add_arguments(
    additional_arguments: list[str], expected_calls: list[_Call]
):
    with (
        patch.object(argparse.ArgumentParser, "add_argument") as mock_add_argument,
        patch.object(CheckArgParser, "__post_init__"),
    ):
        instance = CheckArgParser(
            "unit_test",
            additional_arguments=additional_arguments,
        )
        instance.parser = argparse.ArgumentParser()
        mock_add_argument.reset_mock()
        instance.add_arguments()
        mock_add_argument.assert_has_calls(expected_calls, any_order=True)


MOCK_CWD = Path("unit_test")


@pytest.mark.parametrize(
    argnames=["cli_args", "additional_arguments", "expected_namespace"],
    argvalues=[
        (
            [],
            [],
            argparse.Namespace(
                project_dir=MOCK_CWD,
                manifest_dir=MOCK_CWD / "target",
                catalog_dir=MOCK_CWD / "target",
            ),
        ),
        (
            [
                "test",
                "--project-dir",
                "path/to/project",
                "--include-packages",
                "test_dbt_package",
                "--must-have-all-constraints-from",
                "primary_key",
                "not_null",
                "unique",
            ],
            [
                "include_packages",
                "must_have_all_constraints_from",
            ],
            argparse.Namespace(
                project_dir=Path("path/to/project"),
                manifest_dir=Path("path/to/project/target"),
                catalog_dir=Path("path/to/project/target"),
                include_packages=["test_dbt_package"],
                must_have_all_constraints_from=["primary_key", "not_null", "unique"],
            ),
        ),
    ],
)
def test_dbt_pre_commit_hooks_argument_parser_parse_args(
    cli_args: list[str],
    additional_arguments: list[str],
    expected_namespace: argparse.Namespace,
):
    instance = CheckArgParser(
        "unit_test",
        additional_arguments=additional_arguments,
    )
    with (
        patch.object(sys, "argv", cli_args),
        patch.object(Path, "cwd", return_value=MOCK_CWD),
    ):
        assert instance.parse_args() == expected_namespace
