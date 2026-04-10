"""Argument parser utilities."""

import argparse
import sys
from argparse import Namespace
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Iterable, Type

if TYPE_CHECKING:
    from utils.check_abc import Check


def get_absolute_path(raw_path: str) -> Path:
    """Convert a raw path to an absolute path.

    Relative paths are appended to the current working directory

    Args:
        raw_path: an unconverted path. Can be either relative or absolute.

    Returns:
        an absolute path.
    """
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return (Path.cwd() / path).resolve()


@dataclass
class CliArgument:
    """A Command Line Interface argument.

    Attributes:
        name: Name of the argument
        help: Description of the argument
        type: Type of the argument
        required: Whether the argument is required
        nargs: How to handle multiple values
        default: Default value
    """

    name: str
    help: str
    type: Type | Callable
    required: bool = False
    nargs: str | None = None
    default: Any | None = None

    @property
    def cli_name(self) -> str:
        """Name of the CLI argument."""
        return f"--{self.name.replace('_', '-')}"


UNIVERSAL_ARGUMENTS: tuple[CliArgument, ...] = (
    CliArgument(
        name="project_dir",
        help="Path to the dbt project directory where the dbt_project.yml file is located."
        "Defaults to the current directory.",
        type=get_absolute_path,
        default=Path.cwd().resolve(),
    ),
    CliArgument(
        name="manifest_dir",
        help="Path to the directory containing the dbt manifest.yml file."
        "Defaults to the the 'target' directory underneath the dbt project path.",
        type=Path,
    ),
    CliArgument(
        name="catalog_dir",
        help="Path to the directory containing the dbt catalog.yml file."
        "Defaults to the the 'target' directory underneath the dbt project path.",
        type=Path,
    ),
)
ADDITIONAL_ARGUMENTS: tuple[CliArgument, ...] = (
    CliArgument(
        name="must_have_all_constraints_from",
        help="List of constraint names, from which objects must have all values.",
        type=str,
        nargs="+",
        required=False,
        default=None,
    ),
    CliArgument(
        name="must_have_any_constraint_from",
        help="List of constraint names, from which objects must have at least one value.",
        type=str,
        nargs="+",
        required=False,
        default=None,
    ),
    CliArgument(
        name="must_have_all_data_tests_from",
        help="List of data test names, from which objects must have all values.",
        type=str,
        nargs="+",
        required=False,
        default=None,
    ),
    CliArgument(
        name="must_have_any_data_test_from",
        help="List of data test names, from which objects must have at least one value.",
        type=str,
        nargs="+",
        required=False,
        default=None,
    ),
    CliArgument(
        name="must_have_all_tags_from",
        help="List of tags, from which objects must have all values.",
        type=str,
        nargs="+",
        required=False,
        default=None,
    ),
    CliArgument(
        name="must_have_any_tag_from",
        help="List of values, from which objects must have at least one value.",
        type=str,
        nargs="+",
        required=False,
        default=None,
    ),
    CliArgument(
        name="name_must_match_pattern",
        help="Regex pattern which object name must match.",
        type=str,
        required=False,
        default=None,
    ),
    CliArgument(
        name="must_be_materialized_as_one_of",
        help="Specific materialization names from which models must use one.",
        type=str,
        nargs="+",
        required=False,
        default=None,
    ),
    CliArgument(
        name="include_materializations",
        help="List of materialization types to include. Models with other materialization types will be ignored.",
        type=str,
        nargs="+",
        required=False,
        default=None,
    ),
    CliArgument(
        name="include_packages",
        help="List of packages to include. Nodes not in these packages will be ignored.",
        type=str,
        nargs="+",
        required=False,
        default=None,
    ),
    CliArgument(
        name="include_tags",
        help="List of tags to include. Nodes that do not have at least one of these tags will be ignored.",
        type=str,
        nargs="+",
        required=False,
        default=None,
    ),
    CliArgument(
        name="include_node_paths",
        help="List of resource paths to include. Nodes outside of these paths will be ignored.",
        type=Path,
        nargs="+",
        required=False,
        default=None,
    ),
    CliArgument(
        name="include_name_patterns",
        help="List of name regex patterns to include. Nodes with names not matching any of these regex patterns ignored.",
        type=str,
        nargs="+",
        required=False,
        default=None,
    ),
    CliArgument(
        name="include_direct_parents",
        help="List of direct parent unique IDs to include. Nodes that do not have at least one of these as a direct parent will be ignored.",
        type=str,
        nargs="+",
        required=False,
        default=None,
    ),
    CliArgument(
        name="include_indirect_parents",
        help="List of indirect parent unique IDs to include. Nodes that do not have at least one of these as a direct or indirect parent will be ignored.",
        type=str,
        nargs="+",
        required=False,
        default=None,
    ),
    CliArgument(
        name="include_direct_children",
        help="List of direct child unique IDs to include. Nodes that do not have at least one of these as a direct child will be ignored.",
        type=str,
        nargs="+",
        required=False,
        default=None,
    ),
    CliArgument(
        name="include_indirect_children",
        help="List of indirect child unique IDs to include. Nodes that do not have at least one of these as a direct or indirect child will be ignored.",
        type=str,
        nargs="+",
        required=False,
        default=None,
    ),
    CliArgument(
        name="exclude_materializations",
        help="List of materialization types to exclude. Models with these materialization types will be ignored."
        " Supersedes the 'include_materializations' argument.",
        type=str,
        nargs="+",
        required=False,
        default=None,
    ),
    CliArgument(
        name="exclude_packages",
        help="List of packages to exclude. Nodes in these packages will be ignored."
        " Supersedes the 'include_packages' argument.",
        type=str,
        nargs="+",
        required=False,
        default=None,
    ),
    CliArgument(
        name="exclude_tags",
        help="List of tags to exclude. Nodes that have any of these tags will be ignored."
        " Supersedes the 'include_tags' argument.",
        type=str,
        nargs="+",
        required=False,
        default=None,
    ),
    CliArgument(
        name="exclude_node_paths",
        help="List of node paths to exclude. Nodes under one of these paths will be ignored.",
        type=Path,
        nargs="+",
        required=False,
        default=None,
    ),
    CliArgument(
        name="exclude_name_patterns",
        help="List of name regex patterns to exclude. Nodes with names matching any of these regex patterns ignored.",
        type=str,
        nargs="+",
        required=False,
        default=None,
    ),
    CliArgument(
        name="exclude_direct_parents",
        help="List of direct parent unique IDs to exclude. Nodes with one of these parents will be ignored.",
        type=str,
        nargs="+",
        required=False,
        default=None,
    ),
    CliArgument(
        name="exclude_indirect_parents",
        help="List of indirect parent unique IDs to exclude. Nodes with one of these as either a direct or indirect parents will be ignored.",
        type=str,
        nargs="+",
        required=False,
        default=None,
    ),
    CliArgument(
        name="exclude_direct_children",
        help="List of direct child unique IDs to exclude. Nodes with one of these children will be ignored.",
        type=str,
        nargs="+",
        required=False,
        default=None,
    ),
    CliArgument(
        name="exclude_indirect_children",
        help="List of indirect child unique IDs to exclude. Nodes with one of these as either a direct or indirect child will be ignored.",
        type=str,
        nargs="+",
        required=False,
        default=None,
    ),
)


def parse_cli_entrypoint_args(
    argv: list[str], allowed_checks: Iterable[Type["Check"]]
) -> Namespace:
    """Parse CLI arguments for the entrypoint script.

    Returns:
        Namespace of parsed CLI arguments
    """
    main_parser = argparse.ArgumentParser(
        prog="dbt-review-assistant",
        description="Please choose a check to run, or input 'all-checks' to run every check specified in the config file.",
    )
    subparsers = main_parser.add_subparsers()
    all_checks_parser = subparsers.add_parser(
        "all-checks",
        help="Run all checks",
        prog="all-checks",
    )
    all_checks_parser.set_defaults(check_id="all-checks")
    for check in allowed_checks:
        check_parser = subparsers.add_parser(
            check.check_name,
        )
        check_parser.set_defaults(check_id=check.check_name)
        for argument in UNIVERSAL_ARGUMENTS:
            check_parser.add_argument(
                argument.cli_name,
                type=argument.type,
                help=argument.help,
                nargs=argument.nargs,
                required=argument.required,
                default=argument.default,
            )
        for argument in ADDITIONAL_ARGUMENTS:
            if argument.name in check.additional_arguments:
                check_parser.add_argument(
                    argument.cli_name,
                    type=argument.type,
                    help=argument.help,
                    nargs=argument.nargs,
                    required=argument.required,
                    default=argument.default,
                )
        check_parser.add_argument(
            "-c",
            "--config-dir",
            dest="config_dir",
            help="Path to the directory where the config file is located.",
            type=Path,
        )
        check_parser.add_argument(
            "--files",
            "-f",
            nargs="*",
            help="filepaths passed to the check.",
            type=Path,
        )
    all_checks_parser.add_argument(
        "-c",
        "--config-dir",
        dest="config_dir",
        help="Path to the directory where the config file is located.",
        type=Path,
    )
    all_checks_parser.add_argument(
        dest="files",
        nargs="*",
        help="filepaths passed to the check.",
        type=Path,
    )
    if len(argv) == 0:
        main_parser.print_help(sys.stderr)
        raise SystemExit(1)
    args = main_parser.parse_args(argv)
    if not getattr(args, "config_dir", None):
        args.config_dir = None
    if not getattr(args, "files", None):
        args.files = None
    if not getattr(args, "project_dir", None):
        args.project_dir = Path.cwd()
    if not getattr(args, "manifest_dir", None):
        args.manifest_dir = args.project_dir / "target"
    if not getattr(args, "catalog_dir", None):
        args.catalog_dir = args.manifest_dir
    return args
