import pytest

from utils.manifest_object.macro import Macro, MacroArgument


def test_macro_macro_sql():
    instance = Macro({"macro_sql": "test macro"})
    assert instance.macro_sql == "test macro"


@pytest.mark.parametrize(
    ids=[
        "Two arguments",
        "No arguments",
        "None arguments",
    ],
    argnames=["data", "expected_return"],
    argvalues=[
        (
            {
                "arguments": [
                    {"name": "test_argument"},
                    {"name": "another_argument"},
                ]
            },
            [
                MacroArgument({"name": "test_argument"}),
                MacroArgument({"name": "another_argument"}),
            ],
        ),
        (
            {"arguments": []},
            [],
        ),
        (
            {},
            [],
        ),
    ],
)
def test_macro_arguments(data: dict, expected_return: list[MacroArgument]):
    instance = Macro(data)
    assert list(instance.arguments) == expected_return


@pytest.mark.parametrize(
    ids=[
        "Has type",
        "No type",
        "None type",
    ],
    argnames=["data", "expected_return"],
    argvalues=[
        (
            {"type": "integer"},
            "integer",
        ),
        (
            {},
            None,
        ),
        (
            {"type": None},
            None,
        ),
    ],
)
def test_macro_argument_type(data: dict, expected_return: str | None):
    instance = MacroArgument(data)
    assert instance.type == expected_return


@pytest.mark.parametrize(
    ids=[
        "Has description",
        "No description",
        "None description",
    ],
    argnames=["data", "expected_return"],
    argvalues=[
        (
            {"description": "test_description"},
            "test_description",
        ),
        (
            {},
            None,
        ),
        (
            {"description": None},
            None,
        ),
    ],
)
def test_macro_argument_description(data: dict, expected_return: str | None):
    instance = MacroArgument(data)
    assert instance.description == expected_return
