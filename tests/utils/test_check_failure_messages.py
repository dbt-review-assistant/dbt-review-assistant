from typing import Any

import pytest

from utils.check_failure_messages import (
    dictionary_values_mismatch,
    inconsistent_column_descriptions_message,
    macro_argument_mismatch_manifest_vs_sql,
    manifest_vs_catalog_column_name_mismatch_message,
    manifest_vs_catalog_column_type_mismatch_message,
    object_attribute_value_not_in_set,
    object_missing_attribute_message,
    object_missing_values_from_set_message,
    object_name_does_not_match_pattern,
)


@pytest.mark.parametrize(
    ids=[
        "One model missing description",
        "One source missing data tests",
    ],
    argnames=["kwargs", "expected_return"],
    argvalues=[
        (
            {
                "missing_attributes": ["test_model"],
                "object_type": "model",
                "attribute_type": "description",
            },
            """The following models do not have descriptions:
 - test_model""",
        ),
        (
            {
                "missing_attributes": ["test_source"],
                "object_type": "source",
                "attribute_type": "data test",
                "expected_values": ["unique", "not_null"],
            },
            """The following sources do not have the required  data tests (not_null, unique):
 - test_source""",
        ),
    ],
)
def test_object_missing_attribute_message(kwargs, expected_return):
    assert object_missing_attribute_message(**kwargs) == expected_return


@pytest.mark.parametrize(
    ids=[
        "no match, one arg each",
        "some matching, some mismatch",
    ],
    argnames=["kwargs", "expected_return"],
    argvalues=[
        (
            {
                "sql_args": ["argument_1"],
                "manifest_args": ["argument_2"],
            },
            """There are mismatches between the macro arguments found in the manifest.json and those defined in macro SQL code:
+------------------------------+------------------------------+
|   SQL code macro arguments   |   Manifest macro arguments   |
+------------------------------+------------------------------+
|          argument_1          |           MISSING            |
+------------------------------+------------------------------+
|           MISSING            |          argument_2          |
+------------------------------+------------------------------+""",
        ),
        (
            {
                "sql_args": ["argument_1", "argument_2"],
                "manifest_args": ["argument_2", "argument_3"],
            },
            """There are mismatches between the macro arguments found in the manifest.json and those defined in macro SQL code:
+------------------------------+------------------------------+
|   SQL code macro arguments   |   Manifest macro arguments   |
+------------------------------+------------------------------+
|          argument_1          |           MISSING            |
+------------------------------+------------------------------+
|           MISSING            |          argument_3          |
+------------------------------+------------------------------+""",
        ),
    ],
)
def test_macro_argument_mismatch_manifest_vs_sql(kwargs, expected_return):
    assert macro_argument_mismatch_manifest_vs_sql(**kwargs) == expected_return


@pytest.mark.parametrize(
    ids=[
        "no match, one column each",
        "some match, some mismatch",
    ],
    argnames=["kwargs", "expected_return"],
    argvalues=[
        (
            {
                "manifest_columns": {"column_1"},
                "catalog_columns": {"column_1"},
            },
            """There are mismatches between the column names found in manifest.json vs. catalog.json:
+-----------------+------------------+
| Catalog columns | Manifest columns |
+-----------------+------------------+""",
        ),
        (
            {
                "manifest_columns": {"column_1", "column_2", "column_4"},
                "catalog_columns": {"column_1", "column_2", "column_3"},
            },
            """There are mismatches between the column names found in manifest.json vs. catalog.json:
+------------------------------+------------------------------+
|       Catalog columns        |       Manifest columns       |
+------------------------------+------------------------------+
|           column_3           |           MISSING            |
+------------------------------+------------------------------+
|           MISSING            |           column_4           |
+------------------------------+------------------------------+""",
        ),
    ],
)
def test_manifest_vs_catalog_column_name_mismatch_message(kwargs, expected_return):
    assert manifest_vs_catalog_column_name_mismatch_message(**kwargs) == expected_return


@pytest.mark.parametrize(
    ids=[
        "no match, one column each",
        "some match, some mismatch",
    ],
    argnames=["kwargs", "expected_return"],
    argvalues=[
        (
            {
                "manifest_columns": {"column_1": "INT64"},
                "catalog_columns": {"column_1": "STRING"},
            },
            """There are mismatches between the column types found in manifest.json vs. catalog.json:
+------------------------------+------------------------------+
|       Catalog columns        |       Manifest columns       |
+------------------------------+------------------------------+
|       column_1: STRING       |       column_1: INT64        |
+------------------------------+------------------------------+""",
        ),
        (
            {
                "manifest_columns": {
                    "column_1": "INT64",
                    "column_2": "INT64",
                    "column_4": "INT64",
                },
                "catalog_columns": {
                    "column_1": "INT64",
                    "column_2": "STRING",
                    "column_3": "INT64",
                },
            },
            """There are mismatches between the column types found in manifest.json vs. catalog.json:
+------------------------------+------------------------------+
|       Catalog columns        |       Manifest columns       |
+------------------------------+------------------------------+
|       column_2: STRING       |       column_2: INT64        |
+------------------------------+------------------------------+
|       column_3: INT64        |           MISSING            |
+------------------------------+------------------------------+
|           MISSING            |       column_4: INT64        |
+------------------------------+------------------------------+""",
        ),
    ],
)
def test_manifest_vs_catalog_column_type_mismatch_message(kwargs, expected_return):
    assert manifest_vs_catalog_column_type_mismatch_message(**kwargs) == expected_return


@pytest.mark.parametrize(
    ids=[
        "base case",
    ],
    argnames=["descriptions", "expected_return"],
    argvalues=[
        (
            {
                "column_1": [
                    {"model": "test_model_1", "description": "test description"},
                    {"model": "test_model_2", "description": "another description"},
                ],
                "column_2": [
                    {"model": "test_model_1", "description": "test description"},
                    {"model": "test_model_2", "description": "another description"},
                    {"model": "test_model_3", "description": "yet another description"},
                ],
            },
            """There are inconsistent descriptions for the following model column descriptions:
+-------------------------+-------------------------+-------------------------+
|          Column         |          Model          |       Descriptions      |
+-------------------------+-------------------------+-------------------------+
|         column_1        |       test_model_1      |     test description    |
+-------------------------+-------------------------+-------------------------+
|         column_1        |       test_model_2      |   another description   |
+-------------------------+-------------------------+-------------------------+
|         column_2        |       test_model_1      |     test description    |
+-------------------------+-------------------------+-------------------------+
|         column_2        |       test_model_2      |   another description   |
+-------------------------+-------------------------+-------------------------+
|         column_2        |       test_model_3      | yet another description |
+-------------------------+-------------------------+-------------------------+""",
        ),
    ],
)
def test_inconsistent_column_descriptions_message(
    descriptions: dict[str, list[dict[str, str]]], expected_return: str
):
    assert expected_return == inconsistent_column_descriptions_message(
        descriptions=descriptions
    )


@pytest.mark.parametrize(
    ids=[
        "one model missing tags from must_have_all_from",
        "one model missing data tests from must_have_any_from",
        "one model missing from both must_have_any_from and must_have_all_from",
        "one model with no tags, no required tags",
    ],
    argnames=["kwargs", "expected_return"],
    argvalues=[
        (
            {
                "objects": {"test_model": {"test_tag_5"}},
                "object_type": "model",
                "attribute_type": "tag",
                "must_have_all_from": {"test_tag_1", "test_tag_2"},
                "must_have_any_from": None,
            },
            """The following models do not have the required tags:
+-------------------------+-------------------------+-------------------------+
|          Model          |       Actual tags       |     Require all from    |
+-------------------------+-------------------------+-------------------------+
|        test_model       |      ['test_tag_5']     |      ['test_tag_1',     |
|                         |                         |      'test_tag_2']      |
+-------------------------+-------------------------+-------------------------+""",
        ),
        (
            {
                "objects": {"test_model": {"accepted_values"}},
                "object_type": "model",
                "attribute_type": "data test",
                "must_have_all_from": None,
                "must_have_any_from": {"not_null", "unique"},
            },
            """The following models do not have the required data tests:
+-------------------------+-------------------------+-------------------------+
|          Model          |    Actual data tests    |     Require any from    |
+-------------------------+-------------------------+-------------------------+
|        test_model       |   ['accepted_values']   |  ['not_null', 'unique'] |
+-------------------------+-------------------------+-------------------------+""",
        ),
        (
            {
                "objects": {"test_model": {"test_tag_5"}},
                "object_type": "model",
                "attribute_type": "tag",
                "must_have_all_from": {"test_tag_1", "test_tag_2"},
                "must_have_any_from": {"test_tag_3", "test_tag_4"},
            },
            """The following models do not have the required tags:
+------------------+------------------+------------------+------------------+
|      Model       |   Actual tags    | Require all from | Require any from |
+------------------+------------------+------------------+------------------+
|    test_model    |  ['test_tag_5']  |  ['test_tag_1',  |  ['test_tag_3',  |
|                  |                  |  'test_tag_2']   |  'test_tag_4']   |
+------------------+------------------+------------------+------------------+""",
        ),
        (
            {
                "objects": {"test_model": set()},
                "object_type": "model",
                "attribute_type": "tag",
                "must_have_all_from": None,
                "must_have_any_from": None,
            },
            """The following models do not have tags:
+------------------------------+
|            Model             |
+------------------------------+
|          test_model          |
+------------------------------+""",
        ),
    ],
)
def test_object_missing_values_from_set_message(kwargs: dict, expected_return: str):
    assert expected_return == object_missing_values_from_set_message(**kwargs)


@pytest.mark.parametrize(
    ids=[
        "One model doesn't match",
        "Two sources don't match",
    ],
    argnames=["kwargs", "expected_return"],
    argvalues=[
        (
            {
                "objects": {"test_model"},
                "object_type": "model",
                "name_must_match_pattern": "another_model",
            },
            "The following model names do not match the regex pattern 'another_model':\n"
            " - test_model",
        ),
        (
            {
                "objects": {"test_source", "one_more_source"},
                "object_type": "source",
                "name_must_match_pattern": "another_source",
            },
            "The following source names do not match the regex pattern 'another_source':\n"
            " - one_more_source\n"
            " - test_source",
        ),
    ],
)
def test_object_name_does_not_match_pattern(kwargs: dict, expected_return: str):
    assert object_name_does_not_match_pattern(**kwargs) == expected_return


@pytest.mark.parametrize(
    ids=[
        "One model",
        "Two models",
    ],
    argnames=["kwargs", "expected_return"],
    argvalues=[
        (
            {
                "objects": {"test_model": "ephemeral"},
                "object_type": "model",
                "attribute_type": "materialization",
                "allowed_values": {"table", "view"},
            },
            """The following models do not have an allowed materialization:
+-------------------------+-------------------------+-------------------------+
|          model          |         Allowed         |          Actual         |
+-------------------------+-------------------------+-------------------------+
|        test_model       |          table          |        ephemeral        |
|                         |           view          |                         |
+-------------------------+-------------------------+-------------------------+""",
        ),
        (
            {
                "objects": {"test_model": "ephemeral", "another_model": "incremental"},
                "object_type": "model",
                "attribute_type": "materialization",
                "allowed_values": {"table", "view"},
            },
            """The following models do not have an allowed materialization:
+-------------------------+-------------------------+-------------------------+
|          model          |         Allowed         |          Actual         |
+-------------------------+-------------------------+-------------------------+
|      another_model      |          table          |       incremental       |
|                         |           view          |                         |
+-------------------------+-------------------------+-------------------------+
|        test_model       |          table          |        ephemeral        |
|                         |           view          |                         |
+-------------------------+-------------------------+-------------------------+""",
        ),
    ],
)
def test_object_attribute_value_not_in_set(kwargs: dict, expected_return: str):
    assert object_attribute_value_not_in_set(**kwargs) == expected_return


@pytest.mark.parametrize(
    ids=[
        "One model",
        "Two models",
    ],
    argnames=["kwargs", "expected_return"],
    argvalues=[
        (
            {
                "object_type": "model",
                "dict_name": "config",
                "differences": {
                    "test_model": {
                        "partition_by": {
                            "left": {"granularity": "MONTH"},
                            "right": {"granularity": "DAY"},
                        }
                    }
                },
            },
            """The following models do not have expected config:
+---------------------+--------------------------+----------------------------+
|        model        |         Required         |           Actual           |
+---------------------+--------------------------+----------------------------+
|      test_model     |      partition_by:       |       partition_by:        |
|                     |  {'granularity': 'DAY'}  |  {'granularity': 'MONTH'}  |
+---------------------+--------------------------+----------------------------+""",
        ),
        (
            {
                "object_type": "model",
                "dict_name": "config",
                "differences": {
                    "test_model": {
                        "partition_by": {
                            "left": {"granularity": "MONTH"},
                            "right": {"granularity": "DAY"},
                        }
                    },
                    "another_model": {
                        "incremental_strategy": {
                            "left": "merge",
                            "right": "delete+insert",
                        }
                    },
                },
            },
            """The following models do not have expected config:
+---------------------+--------------------------+----------------------------+
|        model        |         Required         |           Actual           |
+---------------------+--------------------------+----------------------------+
|    another_model    |  incremental_strategy:   |   incremental_strategy:    |
|                     |      delete+insert       |           merge            |
+---------------------+--------------------------+----------------------------+
|      test_model     |      partition_by:       |       partition_by:        |
|                     |  {'granularity': 'DAY'}  |  {'granularity': 'MONTH'}  |
+---------------------+--------------------------+----------------------------+""",
        ),
    ],
)
def test_dictionary_values_mismatch(
    kwargs: dict[str, Any],
    expected_return: str,
):
    assert dictionary_values_mismatch(**kwargs) == expected_return
