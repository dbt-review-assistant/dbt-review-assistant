import sys
from typing import Iterable
from unittest.mock import Mock, patch

import pytest
from jinja2 import Environment

from checks.macro_checks.macro_arguments_match_manifest_vs_sql import (
    MacroArgumentsMatchManifestVsSql,
    Jinja2TestMacroExtension,
    get_macro_args_from_sql_code,
)


@pytest.mark.parametrize(
    ids=[
        "no args",
        "one arg",
        "two args",
        "another unrelated macro in the same file",
    ],
    argnames=("macro", "expected_args"),
    argvalues=(
        (
            {
                "unique_id": "test_macro",
                "macro_sql": "{% macro test_macro() %}...{% endmacro %}",
            },
            set(),
        ),
        (
            {
                "unique_id": "test_macro",
                "macro_sql": "{% macro test_macro(test_arg) %}...{% endmacro %}",
            },
            {"test_arg"},
        ),
        (
            {
                "unique_id": "test_macro",
                "macro_sql": "{% macro test_macro(test_arg1, test_arg2) %}...{% endmacro %}",
            },
            {"test_arg1", "test_arg2"},
        ),
        (
            {
                "unique_id": "test_macro",
                "macro_sql": "{% macro test_macro(test_arg) %}...{% endmacro %}...{% macro another_macro(test_arg) %}...{% endmacro %}",
            },
            {"test_arg"},
        ),
    ),
)
def test_get_macro_args_from_sql_code(macro: dict[str, str], expected_args: set[str]):
    assert get_macro_args_from_sql_code(macro) == expected_args


@pytest.mark.parametrize(
    ids=[
        "generic test with two arguments",
        "generic test with no arguments",
        "macro with no arguments",
        "default argument",
    ],
    argnames=("template_text", "expected_name", "expected_args"),
    argvalues=(
        (
            "{% test test_name(test_arg_1, test_arg_2) %}test body{% endtest %}",
            "test_test_name",
            ["test_arg_1", "test_arg_2"],
        ),
        (
            "{% test another_test_name() %}test body{% endtest %}",
            "test_another_test_name",
            [],
        ),
        (
            "{% macro test_macro() %}test body{% endmacro %}",
            "test_macro",
            [],
        ),
        (
            "{% macro test_macro(default=none) %}test body{% endmacro %}",
            "test_macro",
            ["default"],
        ),
    ),
)
def test_test_jinja2_macro_extension_parse(
    template_text: str, expected_name: str, expected_args: list[str]
):
    env = Environment()
    env.add_extension(Jinja2TestMacroExtension)
    result = env.parse(template_text)
    test = result.body[0]
    assert getattr(test, "name") == expected_name
    assert [arg.name for arg in getattr(test, "args", [])] == expected_args


@pytest.mark.parametrize(
    ids=[
        "no arguments in sql or manifest",
        "one argument in sql and manifest",
        "one argument in sql and two in manifest",
        "one argument in manifest and two in sql",
    ],
    argnames=["macros", "expected_sql_args", "expected_manifest_args"],
    argvalues=[
        (
            [
                {
                    "unique_id": "test_macro",
                    "macro_sql": "{% macro test_macro() %}...{% endmacro %}",
                    "arguments": [],
                },
            ],
            set(),
            set(),
        ),
        (
            [
                {
                    "unique_id": "test_macro",
                    "macro_sql": "{% macro test_macro(argument_1) %}...{% endmacro %}",
                    "arguments": [{"name": "argument_1"}],
                },
            ],
            {"test_macro.argument_1"},
            {"test_macro.argument_1"},
        ),
        (
            [
                {
                    "unique_id": "test_macro",
                    "macro_sql": "{% macro test_macro(argument_1) %}...{% endmacro %}",
                    "arguments": [{"name": "argument_1"}, {"name": "argument_2"}],
                },
            ],
            {"test_macro.argument_1"},
            {"test_macro.argument_1", "test_macro.argument_2"},
        ),
        (
            [
                {
                    "unique_id": "test_macro",
                    "macro_sql": "{% macro test_macro(argument_1, argument_2) %}...{% endmacro %}",
                    "arguments": [{"name": "argument_1"}],
                },
            ],
            {"test_macro.argument_1", "test_macro.argument_2"},
            {"test_macro.argument_1"},
        ),
    ],
)
def test_macro_arguments_match_manifest_vs_sql_perform_checks(
    macros: Iterable[dict[str, str]],
    expected_sql_args: set[str],
    expected_manifest_args: set[str],
    tmpdir,
):
    with (
        patch.object(sys, "argv", return_value=[]),
        patch.object(MacroArgumentsMatchManifestVsSql, "__call__"),
        patch(
            "checks.macro_checks.macro_arguments_match_manifest_vs_sql.get_macros_from_manifest",
            return_value=macros,
        ) as mock_get_macros_from_manifest,
    ):
        instance = MacroArgumentsMatchManifestVsSql()
        instance.perform_check()
        assert instance.check_name == "macro-arguments-match-manifest-vs-sql"
        assert instance.additional_arguments == [
            "include_packages",
            "include_tags",
            "exclude_packages",
            "exclude_tags",
        ]
        assert instance.sql_args == expected_sql_args
        assert instance.manifest_args == expected_manifest_args
        mock_get_macros_from_manifest.assert_called_once_with(
            manifest_dir=instance.args.manifest_dir,
            filter_conditions=instance.filter_conditions,
        )


@pytest.mark.parametrize(
    ids=[
        "no args",
        "one arg, matching",
        "two args, one missing from manifest",
    ],
    argnames=("sql_args", "manifest_args", "expected_result"),
    argvalues=[
        (set(), set(), False),
        ({"argument_1"}, {"argument_1"}, False),
        ({"argument_1", "argument_2"}, {"argument_1"}, True),
    ],
)
def test_macro_arguments_match_manifest_vs_sql_has_failures(
    sql_args: set[str], manifest_args: set[str], expected_result: bool
):
    with (
        patch.object(MacroArgumentsMatchManifestVsSql, "sql_args", sql_args),
        patch.object(MacroArgumentsMatchManifestVsSql, "manifest_args", manifest_args),
        patch.object(MacroArgumentsMatchManifestVsSql, "parse_args"),
        patch.object(MacroArgumentsMatchManifestVsSql, "__call__"),
    ):
        instance = MacroArgumentsMatchManifestVsSql()
        assert expected_result is instance.has_failures


def test_macro_arguments_match_manifest_vs_sql_failure_message():
    with (
        patch.object(MacroArgumentsMatchManifestVsSql, "sql_args"),
        patch.object(MacroArgumentsMatchManifestVsSql, "manifest_args"),
        patch.object(MacroArgumentsMatchManifestVsSql, "parse_args"),
        patch.object(MacroArgumentsMatchManifestVsSql, "__call__"),
        patch(
            "checks.macro_checks.macro_arguments_match_manifest_vs_sql.macro_argument_mismatch_manifest_vs_sql"
        ) as mock_macro_argument_mismatch_manifest_vs_sql,
    ):
        instance = MacroArgumentsMatchManifestVsSql()
        mock_macro_argument_mismatch_manifest_vs_sql.return_value = Mock()
        result = instance.failure_message
        mock_macro_argument_mismatch_manifest_vs_sql.assert_called_with(
            sql_args=instance.sql_args,
            manifest_args=instance.manifest_args,
        )
        assert result is mock_macro_argument_mismatch_manifest_vs_sql.return_value
