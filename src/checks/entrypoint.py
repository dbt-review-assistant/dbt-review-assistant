"""Entrypoint for the CLI."""

import logging
import sys
from argparse import Namespace
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Tuple

from checks import ALL_CHECKS, ALL_CHECKS_MAP
from checks.argparser import parse_cli_entrypoint_args
from utils.config import configure_checks, load_config
from utils.console_formatting import (
    check_status_header,
)


@lru_cache
def convert_to_paths_relative_to_project_dir(
    raw_paths: Tuple[Path, ...], project_dir: Path
) -> list[Path]:
    """Convert a raw path to a path relative to the project directory.

    Paths not in the sub-path of the project directory will not be yielded.

    Args:
        raw_paths: tuple of raw paths to convert.
        project_dir: The project directory absolute path.

    Returns:
        list of Paths relative to the project directory.
    """
    converted_paths = []
    for raw_path in raw_paths:
        abs_path = raw_path if raw_path.is_absolute() else Path.cwd() / raw_path
        try:
            converted_paths.append(abs_path.relative_to(project_dir))
        except ValueError:
            pass
    return converted_paths


def entrypoint() -> None:
    """Entrypoint for the CLI.

    Determines which checks to run and how they are configured.

    Raises:
        SystemExit: with the overall status of all checks
    """
    logging.basicConfig(format="%(message)s", level=logging.INFO)
    cli_args = parse_cli_entrypoint_args(sys.argv[1:], ALL_CHECKS)
    config_data = load_config(cli_args.config_dir) if cli_args.config_dir else None
    all_check_arguments = configure_checks(
        config_data=config_data,
        cli_args=cli_args,
        allowed_checks=ALL_CHECKS,
    )
    for check_args in all_check_arguments:
        if check_args.files:
            check_args.files = convert_to_paths_relative_to_project_dir(
                tuple(check_args.files), check_args.project_dir
            )
    failed_hooks = count_failures(all_check_arguments)
    if failed_hooks:
        raise SystemExit(
            check_status_header(
                f"{failed_hooks}/{len(all_check_arguments)} checks failed",
                False,
            )
        )
    logging.info(
        check_status_header(
            f"{len(all_check_arguments)}/{len(all_check_arguments)} checks passed", True
        )
    )
    raise SystemExit(0)


def count_failures(all_check_arguments: Iterable[Namespace]) -> int:
    """Run each check and compute the sum of check failures.

    Args:
        all_check_arguments: The arguments passed to the checks.

    Returns:
        total number of failed checks.
    """
    failures = 0
    for check_arguments in all_check_arguments:
        result = ALL_CHECKS_MAP[check_arguments.check_id](check_arguments).has_failures
        failures += 0 if result else 1
    return failures
