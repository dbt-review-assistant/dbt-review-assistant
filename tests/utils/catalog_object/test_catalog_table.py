import pytest

from utils.catalog_object.catalog_table import CatalogTable, CatalogColumn


def test_catalog_column_type():
    assert CatalogColumn({"type": "string"}).type == "string"


def test_catalog_column_index():
    assert CatalogColumn({"index": 1}).index == 1


def test_catalog_column_name():
    assert CatalogColumn({"name": "test_name"}).name == "test_name"


@pytest.mark.parametrize(
    ids=["Has comment", "No comment"],
    argnames=[
        "data",
        "expected_return",
    ],
    argvalues=[
        (
            {"comment": "test comment"},
            "test comment",
        ),
        (
            {},
            None,
        ),
    ],
)
def test_catalog_column_comment(data: dict, expected_return: str):
    assert CatalogColumn(data).comment == expected_return


def test_catalog_table_metadata():
    assert CatalogTable({"metadata": {"test": 1}}).metadata == {"test": 1}


def test_catalog_table_stats():
    assert CatalogTable({"stats": {"test": 1}}).stats == {"test": 1}


def test_catalog_table_unique_id():
    assert CatalogTable({"unique_id": "test"}).unique_id == "test"


@pytest.mark.parametrize(
    ids=[
        "Has comment",
        "No comment",
    ],
    argnames=[
        "data",
        "expected_return",
    ],
    argvalues=[
        (
            {"metadata": {"comment": "test comment"}},
            "test comment",
        ),
        (
            {"metadata": {}},
            None,
        ),
    ],
)
def test_catalog_table_comment(data: dict, expected_return: str | None):
    assert CatalogTable(data).comment == expected_return


@pytest.mark.parametrize(
    ids=[
        "Has type",
        "No type",
    ],
    argnames=[
        "data",
        "expected_return",
    ],
    argvalues=[
        (
            {"metadata": {"type": "string"}},
            "string",
        ),
        (
            {"metadata": {}},
            None,
        ),
    ],
)
def test_catalog_table_type(data: dict, expected_return: str | None):
    assert CatalogTable(data).type == expected_return


def test_catalog_table_schema():
    assert CatalogTable({"metadata": {"schema": "test-schema"}}).schema == "test-schema"


def test_catalog_table_name():
    assert CatalogTable({"metadata": {"name": "test-name"}}).name == "test-name"


@pytest.mark.parametrize(
    ids=[
        "Has database",
        "No database",
    ],
    argnames=[
        "data",
        "expected_return",
    ],
    argvalues=[
        (
            {"metadata": {"database": "test-database"}},
            "test-database",
        ),
        (
            {"metadata": {}},
            None,
        ),
    ],
)
def test_catalog_table_database(data: dict, expected_return: str | None):
    assert CatalogTable(data).database == expected_return


@pytest.mark.parametrize(
    ids=[
        "Has owner",
        "No owner",
    ],
    argnames=[
        "data",
        "expected_return",
    ],
    argvalues=[
        (
            {"metadata": {"owner": "test-owner"}},
            "test-owner",
        ),
        (
            {"metadata": {}},
            None,
        ),
    ],
)
def test_catalog_table_owner(data: dict, expected_return: str | None):
    assert CatalogTable(data).owner == expected_return


@pytest.mark.parametrize(
    ids=[
        "Two columns",
        "No columns",
    ],
    argnames=[
        "data",
        "expected_return",
    ],
    argvalues=[
        (
            {
                "unique_id": "test_table",
                "columns": {
                    "column_1": {"name": "column_1"},
                    "column_2": {"name": "column_2"},
                },
            },
            {
                "test_table.column_1": CatalogColumn({"name": "column_1"}),
                "test_table.column_2": CatalogColumn({"name": "column_2"}),
            },
        ),
        (
            {"unique_id": "test_table", "columns": {}},
            {},
        ),
    ],
)
def test_catalog_table_columns(data: dict, expected_return: dict[str, CatalogColumn]):
    assert CatalogTable(data).columns == expected_return
