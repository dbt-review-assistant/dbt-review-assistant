import sys
from argparse import Namespace
from contextlib import nullcontext as does_not_raise
from pathlib import Path
from unittest.mock import patch

import pytest
from _pytest.raises import RaisesExc

from checks import ALL_CHECKS
from checks.argparser import CliArgument, parse_cli_entrypoint_args


@pytest.mark.parametrize(
    ids=[
        "no arguments",
        "check with config_dir",
        "check without config_dir",
        "check with extra args",
    ],
    argnames=["arguments", "expected_result", "expected_raise"],
    argvalues=[
        (
            [],
            None,
            pytest.raises(SystemExit, match="1"),
        ),
        (
            [
                "models-have-descriptions",
                "--config-dir",
                "path/to/project",
            ],
            Namespace(
                project_dir=Path.cwd(),
                manifest_dir=Path.cwd() / "target",
                catalog_dir=Path.cwd() / "target",
                include_materializations=None,
                include_packages=None,
                include_tags=None,
                include_node_paths=None,
                include_name_patterns=None,
                exclude_materializations=None,
                exclude_packages=None,
                exclude_tags=None,
                exclude_node_paths=None,
                exclude_name_patterns=None,
                config_dir=Path("path/to/project"),
                files=None,
                check_id="models-have-descriptions",
            ),
            does_not_raise(),
        ),
        (
            [
                "models-have-descriptions",
            ],
            Namespace(
                project_dir=Path.cwd(),
                manifest_dir=Path.cwd() / "target",
                catalog_dir=Path.cwd() / "target",
                include_materializations=None,
                include_packages=None,
                include_tags=None,
                include_node_paths=None,
                include_name_patterns=None,
                exclude_materializations=None,
                exclude_packages=None,
                exclude_tags=None,
                exclude_node_paths=None,
                exclude_name_patterns=None,
                config_dir=None,
                files=None,
                check_id="models-have-descriptions",
            ),
            does_not_raise(),
        ),
        (
            [
                "models-have-constraints",
                "--config-dir",
                "path/to/project",
                "--must-have-all-constraints-from",
                "primary_key",
            ],
            Namespace(
                project_dir=Path.cwd(),
                manifest_dir=Path.cwd() / "target",
                catalog_dir=Path.cwd() / "target",
                must_have_all_constraints_from=["primary_key"],
                must_have_any_constraint_from=None,
                include_materializations=None,
                include_packages=None,
                include_tags=None,
                include_node_paths=None,
                include_name_patterns=None,
                exclude_materializations=None,
                exclude_packages=None,
                exclude_tags=None,
                exclude_node_paths=None,
                exclude_name_patterns=None,
                config_dir=Path("path/to/project"),
                files=None,
                check_id="models-have-constraints",
            ),
            does_not_raise(),
        ),
    ],
)
def test_parse_cli_entrypoint_args(
    arguments: list[str],
    expected_result: tuple[Namespace, list[str]],
    expected_raise: does_not_raise | RaisesExc[BaseException],
):
    with (
        expected_raise as e,
        patch("checks.argparser.argparse.ArgumentParser.print_help") as mock_print_help,
    ):
        assert parse_cli_entrypoint_args(arguments, ALL_CHECKS) == expected_result
    if e:
        mock_print_help.assert_called_with(sys.stderr)


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
