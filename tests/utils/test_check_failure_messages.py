import pytest

from utils.check_failure_messages import (
    macro_argument_mismatch_manifest_vs_sql,
    manifest_vs_catalog_column_name_mismatch_message,
    object_missing_attribute_message,
    manifest_vs_catalog_column_type_mismatch_message,
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
                "manifest_columns": {"column_1", "column_2"},
                "catalog_columns": {"column_1", "column_2", "column_3"},
            },
            """There are mismatches between the column names found in manifest.json vs. catalog.json:
+------------------------------+------------------------------+
|       Catalog columns        |       Manifest columns       |
+------------------------------+------------------------------+
|           column_3           |           MISSING            |
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
                "manifest_columns": {"column_1": "INT64", "column_2": "INT64"},
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
+------------------------------+------------------------------+""",
        ),
    ],
)
def test_manifest_vs_catalog_column_type_mismatch_message(kwargs, expected_return):
    assert manifest_vs_catalog_column_type_mismatch_message(**kwargs) == expected_return
