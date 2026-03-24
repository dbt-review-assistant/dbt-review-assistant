"""Check configuration utilities."""

import logging
from argparse import Namespace
from pathlib import Path
from typing import TYPE_CHECKING, Any, Collection, Iterable, Type

import yaml
from jsonschema import validate

from checks.argparser import parse_cli_entrypoint_args

if TYPE_CHECKING:
    from utils.check_abc import Check

CONFIG_YAML_SCHEMA = """
type: object
properties:
    global_arguments:
        type: object
        additionalProperties: false
        properties:
            arguments:
                type: array
        
    per_check_arguments:
        type: array
        items:
            type: object
            required: ["check_id"]
            additionalProperties: false
            properties:
                check_id:
                    type: string
                arguments:
                    type: array
                    items:
                        type: string
                description:
                    type: string
"""

PROJECT_NAME = "dbt-review-assistant"


def load_config(config_dir: Path) -> dict[str, Any]:
    """Load configuration data from the YAML file.

    Args:
        config_dir: Path to the directory where the configuration file is located

    Returns:
        a dictionary of configuration data

    Raises:
        FileNotFoundError: if an unknown hook is called,
    """
    file_path = config_dir / f".{PROJECT_NAME}.yaml"
    if not file_path.is_file():
        raise FileNotFoundError(f"{file_path} not found.")
    with open(file_path) as f:
        loader = yaml.SafeLoader
        config_data = yaml.load(f, Loader=loader)
        validate(config_data, yaml.load(CONFIG_YAML_SCHEMA, Loader=loader))
    return config_data


def configure_checks(
    config_data: dict | None,
    cli_args: Namespace,
    allowed_checks: Iterable[Type["Check"]],
) -> list[Namespace]:
    """Configure checks using CLI arguments or the config file data, if found.

    Args:
        config_data: Optional, configuration data from the config file.
            Defaults to None
        cli_args: CLI arguments from the main entrypoint command
        allowed_checks: Collection of Check objects which can be selected from

    Returns:
        list of check arguments to be run
    """
    if config_data:
        global_options = config_data.get("global_arguments", {}).get("arguments", [])
        check_instances: list[Namespace] = []
        for check_instance in config_data.get("per_check_arguments", []):
            if (
                check_instance["check_id"] == cli_args.check_id
                or cli_args.check_id == "all-checks"
            ):
                argv = (
                    [check_instance["check_id"]]
                    + global_options
                    + check_instance.get("arguments", [])
                )
                files = getattr(cli_args, "files")
                if files:
                    argv += ["--files"] + [file.as_posix() for file in files]
                check_instances.append(parse_cli_entrypoint_args(argv, allowed_checks))
        # if check instance not found in config, run it without any arguments
        if not check_instances:
            logging.warning(
                f"Check '{cli_args.check_id}' not found in "
                f"{cli_args.config_dir.absolute() / f'.{PROJECT_NAME}.yaml'}.\n"
                "Running without arguments..."
            )
            check_instances = [cli_args]
    elif cli_args.check_id == "all-checks" and not config_data:
        raise RuntimeError("Check id 'all-checks' requires a config file.")
    else:
        # Get the config from the CLI args if no config provided
        check_instances = [cli_args]
    return check_instances
