import logging
import re
import sys
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

import pytest

from checks import ModelsHaveColumns, ModelsHaveDescriptions
from checks.entrypoint import (
    convert_to_paths_relative_to_project_dir,
    count_failures,
    entrypoint,
)
from utils.console_formatting import check_status_header


@pytest.mark.parametrize(
    ids=[
        "no check-id, no config",
        "one pass, one fail",
        "two fail",
        "two pass",
        "one pass",
        "one fail",
    ],
    argnames=[
        "arguments",
        "failures",
        "config_data",
        "expected_check_arguments",
        "expected_raise",
        "expected_info_msg",
    ],
    argvalues=[
        (
            [
                "test",
            ],
            0,
            None,
            [],
            pytest.raises(
                SystemExit,
                match=re.escape("0"),
            ),
            None,
        ),
        (
            [
                "test",
                "all-checks",
                "-c",
                ".",
                "path/to/project/test.sql",
                "path/to/project/test.yml",
                "foo.txt",
            ],
            1,
            {
                "global_arguments": {
                    "arguments": [
                        "--project-dir",
                        (Path.cwd() / "path/to/project/").as_posix(),
                    ],
                },
                "per_check_arguments": [
                    {"check_id": "models-have-descriptions"},
                    {"check_id": "models-have-constraints"},
                ],
            },
            [
                Namespace(
                    project_dir=Path.cwd() / "path/to/project/",
                    manifest_dir=Path.cwd() / "path/to/project/target/",
                    catalog_dir=Path.cwd() / "path/to/project/target/",
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
                    files=[Path("test.sql"), Path("test.yml")],
                    check_id="models-have-descriptions",
                ),
                Namespace(
                    project_dir=Path.cwd() / "path/to/project/",
                    manifest_dir=Path.cwd() / "path/to/project/target/",
                    catalog_dir=Path.cwd() / "path/to/project/target/",
                    must_have_all_constraints_from=None,
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
                    config_dir=None,
                    files=[Path("test.sql"), Path("test.yml")],
                    check_id="models-have-constraints",
                ),
            ],
            pytest.raises(
                SystemExit,
                match=re.escape(check_status_header("1/2 checks failed", False)),
            ),
            None,
        ),
        (
            [
                "test",
                "all-checks",
                "-c",
                ".",
                "path/to/project/test.sql",
                "path/to/project/test.yml",
                "foo.txt",
            ],
            2,
            {
                "global_arguments": {
                    "arguments": [
                        "--project-dir",
                        (Path.cwd() / "path/to/project/").as_posix(),
                    ],
                },
                "per_check_arguments": [
                    {"check_id": "models-have-descriptions"},
                    {"check_id": "models-have-constraints"},
                ],
            },
            [
                Namespace(
                    project_dir=Path.cwd() / "path/to/project/",
                    manifest_dir=Path.cwd() / "path/to/project/target/",
                    catalog_dir=Path.cwd() / "path/to/project/target/",
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
                    files=[Path("test.sql"), Path("test.yml")],
                    check_id="models-have-descriptions",
                ),
                Namespace(
                    project_dir=Path.cwd() / "path/to/project/",
                    manifest_dir=Path.cwd() / "path/to/project/target/",
                    catalog_dir=Path.cwd() / "path/to/project/target/",
                    must_have_all_constraints_from=None,
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
                    config_dir=None,
                    files=[Path("test.sql"), Path("test.yml")],
                    check_id="models-have-constraints",
                ),
            ],
            pytest.raises(
                SystemExit,
                match=re.escape(check_status_header("2/2 checks failed", False)),
            ),
            None,
        ),
        (
            [
                "test",
                "all-checks",
                "-c",
                ".",
                "path/to/project/test.sql",
                "path/to/project/test.yml",
                "foo.txt",
            ],
            0,
            {
                "global_arguments": {
                    "arguments": [
                        "--project-dir",
                        (Path.cwd() / "path/to/project/").as_posix(),
                    ],
                },
                "per_check_arguments": [
                    {"check_id": "models-have-descriptions"},
                    {"check_id": "models-have-constraints"},
                ],
            },
            [
                Namespace(
                    project_dir=Path.cwd() / "path/to/project/",
                    manifest_dir=Path.cwd() / "path/to/project/target/",
                    catalog_dir=Path.cwd() / "path/to/project/target/",
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
                    files=[Path("test.sql"), Path("test.yml")],
                    check_id="models-have-descriptions",
                ),
                Namespace(
                    project_dir=Path.cwd() / "path/to/project/",
                    manifest_dir=Path.cwd() / "path/to/project/target/",
                    catalog_dir=Path.cwd() / "path/to/project/target/",
                    must_have_all_constraints_from=None,
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
                    config_dir=None,
                    files=[Path("test.sql"), Path("test.yml")],
                    check_id="models-have-constraints",
                ),
            ],
            pytest.raises(
                SystemExit,
                match="0",
            ),
            check_status_header("2/2 checks passed", True),
        ),
        (
            [
                "test",
                "all-checks",
                "-c",
                ".",
                "path/to/project/test.sql",
                "path/to/project/test.yml",
                "foo.txt",
            ],
            0,
            {
                "global_arguments": {
                    "arguments": [
                        "--project-dir",
                        (Path.cwd() / "path/to/project/").as_posix(),
                    ],
                },
                "per_check_arguments": [
                    {"check_id": "models-have-descriptions"},
                ],
            },
            [
                Namespace(
                    project_dir=Path.cwd() / "path/to/project/",
                    manifest_dir=Path.cwd() / "path/to/project/target/",
                    catalog_dir=Path.cwd() / "path/to/project/target/",
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
                    files=[Path("test.sql"), Path("test.yml")],
                    check_id="models-have-descriptions",
                ),
            ],
            pytest.raises(
                SystemExit,
                match="0",
            ),
            check_status_header("1/1 checks passed", True),
        ),
        (
            [
                "test",
                "all-checks",
                "-c",
                ".",
                "path/to/project/test.sql",
                "path/to/project/test.yml",
                "foo.txt",
            ],
            1,
            {
                "global_arguments": {
                    "arguments": [
                        "--project-dir",
                        (Path.cwd() / "path/to/project/").as_posix(),
                    ],
                },
                "per_check_arguments": [
                    {"check_id": "models-have-descriptions"},
                ],
            },
            [
                Namespace(
                    project_dir=Path.cwd() / "path/to/project/",
                    manifest_dir=Path.cwd() / "path/to/project/target/",
                    catalog_dir=Path.cwd() / "path/to/project/target/",
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
                    files=[Path("test.sql"), Path("test.yml")],
                    check_id="models-have-descriptions",
                ),
            ],
            pytest.raises(
                SystemExit,
                match=re.escape(check_status_header("1/1 checks failed", False)),
            ),
            None,
        ),
    ],
)
def test_entrypoint(
    arguments,
    failures,
    config_data,
    expected_check_arguments,
    expected_raise,
    expected_info_msg,
):
    with (
        expected_raise,
        patch.object(sys, "argv", arguments),
        patch.object(logging, "info") as mock_info,
        patch("checks.entrypoint.load_config", return_value=config_data),
        patch(
            "checks.entrypoint.count_failures", return_value=failures
        ) as mock_count_failures,
    ):
        entrypoint()
    if expected_info_msg:
        mock_info.assert_called_with(expected_info_msg)
    mock_count_failures.assert_called_with(expected_check_arguments)


def test_convert_to_paths_relative_to_project_dir():
    raw_paths = (
        Path("outside_project_relative"),
        Path("/outside_project_absolute"),
        Path("outside_project_relative"),
        Path.cwd() / "path/to/project/inside_project_absolute.sql",
        Path("path/to/project/inside_project_absolute.sql"),
    )
    expected_paths = [
        Path("inside_project_absolute.sql"),
        Path("inside_project_absolute.sql"),
    ]
    project_dir = Path.cwd() / "path/to/project"
    assert (
        list(convert_to_paths_relative_to_project_dir(raw_paths, project_dir))
        == expected_paths
    )


def test_count_failures():
    all_arguments = [
        Namespace(check_id="models-have-descriptions"),
        Namespace(check_id="models-have-columns"),
    ]
    with (
        patch.object(ModelsHaveDescriptions, "failures", False),
        patch.object(
            ModelsHaveDescriptions, "__init__", return_value=None
        ) as mock_init_1,
        patch.object(ModelsHaveColumns, "failures", True),
        patch.object(ModelsHaveColumns, "__init__", return_value=None) as mock_init_2,
    ):
        actual = count_failures(all_arguments)
        assert actual == 1
        mock_init_1.assert_called_with(all_arguments[0])
        mock_init_2.assert_called_with(all_arguments[1])
