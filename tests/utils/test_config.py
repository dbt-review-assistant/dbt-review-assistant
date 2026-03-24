import logging
import re
from argparse import Namespace
from contextlib import nullcontext as does_not_raise
from pathlib import Path
from unittest.mock import call, patch

import pytest
from jsonschema import ValidationError

from checks import ALL_CHECKS
from utils.config import PROJECT_NAME, configure_checks, load_config

VALID_MANIFEST = """
global_arguments:
  arguments: [
    "--project-dir",
    "path/to/project",
    "--include-packages",
    "test_dbt_package",
  ]
per_check_arguments:
  - check_id: models-have-descriptions
  - check_id: models-have-constraints
    arguments: [
      "--must-have-all-constraints-from",
      "primary_key",
      "--include-materializations",
      "view",
    ]
"""

INVALID_MANIFEST = """
global_arguments:
  arguments: [
    "--project-dir",
    "path/to/project",
    "--include-packages",
    "test_dbt_package",
  ]
per_check_arguments:
  - wrong_key: models-have-descriptions
  - check_id: models-have-constraints
    arguments: [
      "--must-have-all-constraints-from",
      "primary_key",
      "--include-materializations",
      "view",
    ]
"""


@pytest.mark.parametrize(
    ids=["valid manifest", "invalid manifest", "file not found"],
    argnames=[
        "config_dir",
        "manifest_contents",
        "expected_return",
        "expected_raise",
    ],
    argvalues=[
        (
            Path("path/to/project"),
            VALID_MANIFEST,
            {
                "global_arguments": {
                    "arguments": [
                        "--project-dir",
                        "path/to/project",
                        "--include-packages",
                        "test_dbt_package",
                    ],
                },
                "per_check_arguments": [
                    {
                        "check_id": "models-have-descriptions",
                    },
                    {
                        "arguments": [
                            "--must-have-all-constraints-from",
                            "primary_key",
                            "--include-materializations",
                            "view",
                        ],
                        "check_id": "models-have-constraints",
                    },
                ],
            },
            does_not_raise(),
        ),
        (
            Path("path/to/project"),
            INVALID_MANIFEST,
            {},
            pytest.raises(ValidationError, match="'check_id' is a required property"),
        ),
        (
            Path("wrong/path"),
            VALID_MANIFEST,
            {},
            pytest.raises(
                FileNotFoundError,
                match=re.escape(
                    str(Path("wrong/path/.dbt-review-assistant.yaml not found."))
                ),
            ),
        ),
    ],
)
def test_load_config(
    config_dir, manifest_contents, expected_return, expected_raise, tmpdir
):
    path = Path(tmpdir) / "path/to/project"
    path.mkdir(parents=True, exist_ok=True)
    with open(path / f".{PROJECT_NAME}.yaml", "w") as f:
        f.write(manifest_contents)
    with expected_raise:
        assert load_config(Path(tmpdir) / config_dir) == expected_return


@pytest.mark.parametrize(
    ids=[
        "one check",
        "all checks",
        "check not in config",
        "all without config file",
        "one check with no config",
    ],
    argnames=[
        "config_data",
        "args",
        "expected_return",
        "expected_raise",
        "expected_warning",
    ],
    argvalues=[
        (
            {
                "global_arguments": {
                    "arguments": [
                        "--project-dir",
                        "path/to/project",
                        "--include-packages",
                        "test_dbt_package",
                    ],
                },
                "per_check_arguments": [
                    {
                        "check_id": "models-have-descriptions",
                    },
                    {
                        "arguments": [
                            "--must-have-all-constraints-from",
                            "primary_key",
                            "--include-materializations",
                            "view",
                        ],
                        "check_id": "models-have-constraints",
                    },
                ],
            },
            Namespace(
                config_dir=Path("path/to/project"),
                check_id="models-have-descriptions",
                files=None,
            ),
            [
                Namespace(
                    project_dir=Path.cwd() / Path("path/to/project"),
                    manifest_dir=Path.cwd() / Path("path/to/project/target"),
                    catalog_dir=Path.cwd() / Path("path/to/project/target"),
                    include_materializations=None,
                    include_packages=["test_dbt_package"],
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
                )
            ],
            does_not_raise(),
            None,
        ),
        (
            {
                "global_arguments": {
                    "arguments": [
                        "--project-dir",
                        "path/to/project",
                        "--include-packages",
                        "test_dbt_package",
                    ],
                },
                "per_check_arguments": [
                    {
                        "check_id": "models-have-descriptions",
                    },
                    {
                        "arguments": [
                            "--must-have-all-constraints-from",
                            "primary_key",
                            "--include-materializations",
                            "view",
                        ],
                        "check_id": "models-have-constraints",
                    },
                ],
            },
            Namespace(
                config_dir=Path("path/to/project"),
                check_id="all-checks",
                files=[Path("test.sql"), Path("test.yml")],
            ),
            [
                Namespace(
                    project_dir=Path.cwd() / Path("path/to/project"),
                    manifest_dir=Path.cwd() / Path("path/to/project/target"),
                    catalog_dir=Path.cwd() / Path("path/to/project/target"),
                    include_materializations=None,
                    include_packages=["test_dbt_package"],
                    include_tags=None,
                    include_node_paths=None,
                    include_name_patterns=None,
                    exclude_materializations=None,
                    exclude_packages=None,
                    exclude_tags=None,
                    exclude_node_paths=None,
                    exclude_name_patterns=None,
                    config_dir=None,
                    files=[Path("test.sql"), Path("test.yml")],
                    check_id="models-have-descriptions",
                ),
                Namespace(
                    project_dir=Path.cwd() / Path("path/to/project"),
                    manifest_dir=Path.cwd() / Path("path/to/project/target"),
                    catalog_dir=Path.cwd() / Path("path/to/project/target"),
                    must_have_all_constraints_from=["primary_key"],
                    must_have_any_constraint_from=None,
                    include_materializations=["view"],
                    include_packages=["test_dbt_package"],
                    include_tags=None,
                    include_node_paths=None,
                    include_name_patterns=None,
                    exclude_materializations=None,
                    exclude_packages=None,
                    exclude_tags=None,
                    exclude_node_paths=None,
                    exclude_name_patterns=None,
                    config_dir=None,
                    files=[Path("test.sql"), Path("test.yml")],
                    check_id="models-have-constraints",
                ),
            ],
            does_not_raise(),
            None,
        ),
        (
            {
                "global_arguments": {
                    "arguments": [
                        "--project-dir",
                        "path/to/project",
                        "--include-packages",
                        "test_dbt_package",
                    ],
                },
                "per_check_arguments": [
                    {
                        "check_id": "models-have-descriptions",
                    },
                    {
                        "arguments": [
                            "--must-have-all-constraints-from",
                            "primary_key",
                            "--include-materializations",
                            "view",
                        ],
                        "check_id": "models-have-constraints",
                    },
                ],
            },
            Namespace(
                config_dir=Path("path/to/project"),
                check_id="models-have-data-tests",
                files=None,
            ),
            [
                Namespace(
                    config_dir=Path("path/to/project"),
                    check_id="models-have-data-tests",
                    files=None,
                )
            ],
            does_not_raise(),
            f"Check 'models-have-data-tests' not found in {(Path.cwd() / Path(f'path/to/project/.{PROJECT_NAME}.yaml')).as_posix()}.\nRunning without arguments...",
        ),
        (
            None,
            Namespace(
                config_dir=Path("path/to/project"),
                check_id="all-checks",
                files=None,
            ),
            [],
            pytest.raises(
                RuntimeError, match="Check id 'all-checks' requires a config file."
            ),
            None,
        ),
        (
            None,
            Namespace(
                config_dir=Path("path/to/project"),
                check_id="models-have-descriptions",
                files=None,
            ),
            [
                Namespace(
                    config_dir=Path("path/to/project"),
                    check_id="models-have-descriptions",
                    files=None,
                )
            ],
            does_not_raise(),
            None,
        ),
    ],
)
def test_configure_checks(
    config_data, args, expected_return, expected_raise, expected_warning
):
    with expected_raise, patch.object(logging, "warning") as mock_warning:
        result = configure_checks(
            config_data=config_data,
            cli_args=args,
            allowed_checks=ALL_CHECKS,
        )
        assert result == expected_return
        if expected_warning:
            mock_warning.assert_called_with(expected_warning)
