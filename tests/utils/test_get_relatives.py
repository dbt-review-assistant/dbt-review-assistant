from unittest.mock import Mock

import pytest

from utils.get_relatives import (
    get_all_children,
    get_all_parents,
    get_direct_children,
    get_direct_parents,
)


@pytest.mark.parametrize(
    argnames=["unique_id", "parent_map", "expected"],
    ids=["has direct parents", "No parents", "Not in parent_map"],
    argvalues=[
        (
            "test_model",
            {"test_model": ["another_model"]},
            {"another_model"},
        ),
        (
            "test_model",
            {"test_model": []},
            set(),
        ),
        (
            "test_model",
            {},
            set(),
        ),
    ],
)
def test_get_direct_parents(
    unique_id: str,
    parent_map: dict[str, list[str]],
    expected: set[str],
):
    manifest = Mock()
    manifest.parent_map = parent_map
    result = get_direct_parents(unique_id=unique_id, manifest=manifest)
    assert result == expected


@pytest.mark.parametrize(
    argnames=["unique_id", "child_map", "expected"],
    ids=["has direct parents", "No parents", "Not in child_map"],
    argvalues=[
        (
            "test_model",
            {"test_model": ["another_model"]},
            {"another_model"},
        ),
        (
            "test_model",
            {"test_model": []},
            set(),
        ),
        (
            "test_model",
            {},
            set(),
        ),
    ],
)
def test_get_direct_children(
    unique_id: str,
    child_map: dict[str, list[str]],
    expected: set[str],
):
    manifest = Mock()
    manifest.child_map = child_map
    result = get_direct_children(unique_id=unique_id, manifest=manifest)
    assert result == expected


@pytest.mark.parametrize(
    argnames=["unique_id", "parent_map", "include_indirect", "expected"],
    ids=[
        "Has only direct parents",
        "No parents",
        "Not in parent_map",
        "Has indirect parents - include indirect",
        "Has indirect parents - exclude indirect",
    ],
    argvalues=[
        (
            "test_model",
            {"test_model": ["another_model"]},
            True,
            {"another_model"},
        ),
        (
            "test_model",
            {"test_model": []},
            True,
            set(),
        ),
        (
            "test_model",
            {},
            True,
            set(),
        ),
        (
            "test_model",
            {
                "test_model": ["another_model"],
                "another_model": ["one_more_model"],
                "one_more_model": [],
            },
            True,
            {"another_model", "one_more_model"},
        ),
        (
            "test_model",
            {
                "test_model": ["another_model"],
                "another_model": ["one_more_model"],
                "one_more_model": [],
            },
            False,
            {"another_model"},
        ),
    ],
)
def test_get_all_parents(
    unique_id: str,
    parent_map: dict[str, list[str]],
    include_indirect: bool,
    expected: set[str],
):
    manifest = Mock()
    manifest.parent_map = parent_map
    result = get_all_parents(
        unique_id=unique_id,
        manifest=manifest,
        include_indirect=include_indirect,
    )
    assert result == expected


@pytest.mark.parametrize(
    argnames=["unique_id", "child_map", "include_indirect", "expected"],
    ids=[
        "Has only direct children",
        "No children",
        "Not in child_map",
        "Has indirect children - include indirect",
        "Has indirect children - exclude indirect",
    ],
    argvalues=[
        (
            "test_model",
            {"test_model": ["another_model"]},
            True,
            {"another_model"},
        ),
        (
            "test_model",
            {"test_model": []},
            True,
            set(),
        ),
        (
            "test_model",
            {},
            True,
            set(),
        ),
        (
            "test_model",
            {
                "test_model": ["another_model"],
                "another_model": ["one_more_model"],
                "one_more_model": [],
            },
            True,
            {"another_model", "one_more_model"},
        ),
        (
            "test_model",
            {
                "test_model": ["another_model"],
                "another_model": ["one_more_model"],
                "one_more_model": [],
            },
            False,
            {"another_model"},
        ),
    ],
)
def test_get_all_children(
    unique_id: str,
    child_map: dict[str, list[str]],
    include_indirect: bool,
    expected: set[str],
):
    manifest = Mock()
    manifest.child_map = child_map
    result = get_all_children(
        unique_id=unique_id,
        manifest=manifest,
        include_indirect=include_indirect,
    )
    assert result == expected
