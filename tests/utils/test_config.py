import logging
import re
from argparse import Namespace
from contextlib import nullcontext
from pathlib import Path
from unittest.mock import call, patch

import pytest
from jsonschema import ValidationError

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
      "--constraints",
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
      "--constraints",
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
    ],
    argvalues=[
        (
            Path("path/to/project"),
            VALID_MANIFEST,
            nullcontext(
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
                                "--constraints",
                                "primary_key",
                                "--include-materializations",
                                "view",
                            ],
                            "check_id": "models-have-constraints",
                        },
                    ],
                }
            ),
        ),
        (
            Path("path/to/project"),
            INVALID_MANIFEST,
            pytest.raises(ValidationError, match="'check_id' is a required property"),
        ),
        (
            Path("wrong/path"),
            VALID_MANIFEST,
            pytest.raises(
                FileNotFoundError,
                match=re.escape(
                    str(Path("wrong/path/.dbt-review-assistant.yaml not found."))
                ),
            ),
        ),
    ],
)
def test_load_config(config_dir, manifest_contents, expected_return, tmpdir):
    path = Path(tmpdir) / "path/to/project"
    path.mkdir(parents=True, exist_ok=True)
    with open(path / f".{PROJECT_NAME}.yaml", "w") as f:
        f.write(manifest_contents)
    with expected_return as e:
        assert load_config(Path(tmpdir) / config_dir) == e


@pytest.mark.parametrize(
    ids=[
        "one check",
        "all checks",
        "check not in config",
        "all without config file",
        "one check with no config",
        "config data and extra args",
    ],
    argnames=[
        "config_data",
        "known_args",
        "extra_args",
        "expected_return",
        "expect_warning",
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
                            "--constraints",
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
            ),
            [],
            nullcontext(
                [
                    [
                        "models-have-descriptions",
                        "--project-dir",
                        "path/to/project",
                        "--include-packages",
                        "test_dbt_package",
                    ]
                ]
            ),
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
                            "--constraints",
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
            ),
            [],
            nullcontext(
                [
                    [
                        "models-have-descriptions",
                        "--project-dir",
                        "path/to/project",
                        "--include-packages",
                        "test_dbt_package",
                    ],
                    [
                        "models-have-constraints",
                        "--project-dir",
                        "path/to/project",
                        "--include-packages",
                        "test_dbt_package",
                        "--constraints",
                        "primary_key",
                        "--include-materializations",
                        "view",
                    ],
                ]
            ),
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
                            "--constraints",
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
            ),
            [],
            nullcontext(
                [
                    [
                        "models-have-data-tests",
                    ]
                ]
            ),
            True,
        ),
        (
            None,
            Namespace(
                config_dir=Path("path/to/project"),
                check_id="all-checks",
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
            ),
            ["--packages", "test_dbt_package"],
            nullcontext(
                [["models-have-descriptions", "--packages", "test_dbt_package"]]
            ),
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
                            "--constraints",
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
            ),
            ["--packages", "test_dbt_package"],
            nullcontext(
                [
                    [
                        "models-have-descriptions",
                        "--project-dir",
                        "path/to/project",
                        "--include-packages",
                        "test_dbt_package",
                    ]
                ]
            ),
            True,
        ),
    ],
)
def test_configure_checks(
    config_data, known_args, extra_args, expected_return, expect_warning
):
    with expected_return as e, patch.object(logging, "warning") as mock_warning:
        result = configure_checks(
            config_data=config_data,
            known_args=known_args,
            extra_args=extra_args,
        )
        assert result == e
        expected_warning_calls = []
        filename = f".{PROJECT_NAME}.yaml"
        if expect_warning and config_data and extra_args:
            expected_warning_calls.append(
                call(
                    f"Check configuration will be read from {(known_args.config_dir / filename).absolute()}, therefore the following extra CLI arguments will be ignored: ['--packages', 'test_dbt_package']"
                )
            )
        elif expect_warning:
            expected_warning_calls.append(
                call(
                    f"Check 'models-have-data-tests' not found in {(known_args.config_dir / filename).absolute()}.\nRunning without arguments..."
                )
            )
        mock_warning.assert_has_calls(expected_warning_calls)
