from argparse import Namespace
from contextlib import nullcontext
from pathlib import Path

import pytest
from jsonschema import ValidationError

from utils.config import load_config, configure_checks, PROJECT_NAME

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
                match=str(Path("wrong/path/.dbt-review-assistant.yaml not found.")),
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
    ],
    argnames=["config_data", "known_args", "extra_args", "expected_return"],
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
        ),
    ],
)
def test_configure_checks(config_data, known_args, extra_args, expected_return):
    with expected_return as e:
        result = configure_checks(
            config_data=config_data,
            known_args=known_args,
            extra_args=extra_args,
        )
        assert result == e
