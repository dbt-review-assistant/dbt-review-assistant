from pathlib import Path

import pytest

from utils.manifest_object.manifest_object import (
    HasPatchPathMixin,
    ManifestObject,
    TaggableMixin,
)
from utils.manifest_object.node.node import ManifestNode


class ConcreteManifestNode(ManifestNode):
    pass


class ConcreteTaggableNode(TaggableMixin, ManifestObject):
    pass


class ConcreteHasPatchPathNode(HasPatchPathMixin, ManifestObject):
    pass


@pytest.mark.parametrize(
    ids=[
        "Has patch path",
        "No patch path",
        "None patch path",
    ],
    argnames=["data", "expected_return"],
    argvalues=[
        (
            {
                "package_name": "test_package",
                "patch_path": "test_package://path/to/model.sql",
            },
            Path("path/to/model.sql"),
        ),
        (
            {},
            None,
        ),
        (
            {"package_name": "test_package", "patch_path": None},
            None,
        ),
    ],
)
def test_has_patch_path_patch_path(data: dict, expected_return: Path | None):
    instance = ConcreteHasPatchPathNode(data)
    assert instance.patch_path == expected_return


@pytest.mark.parametrize(
    argnames=["data", "expected_return"],
    ids=[
        "Has top-level tags",
        "Has config-level tags",
        "Has tags at both levels",
        "Has empty tags",
        "Tags property missing",
    ],
    argvalues=[
        ({"tags": ["tag1", "tag2"]}, {"tag1", "tag2"}),
        ({"config": {"tags": ["tag1", "tag2"]}}, {"tag1", "tag2"}),
        (
            {"tags": ["tag1", "tag2"], "config": {"tags": ["tag3", "tag4"]}},
            {"tag1", "tag2", "tag3", "tag4"},
        ),
        ({"tags": [], "config": {"tags": []}}, set()),
        ({}, set()),
    ],
)
def test_taggable_mixin_tags(data: dict, expected_return: set[str]):
    instance = ConcreteTaggableNode(data)
    assert instance.tags == expected_return


@pytest.mark.parametrize(
    argnames=[
        "data",
        "must_have_all_tags_from",
        "must_have_any_tags_from",
        "expected_return",
    ],
    ids=[
        "Has two from 'must_have_all_tags_from'",
        "Has one from 'must_have_all_tags_from'",
        "Has two from 'must_have_any_tags_from'",
        "Has one from 'must_have_any_tags_from'",
        "Has none from 'must_have_any_tags_from'",
        "Has two from 'must_have_all_tags_from' and one from 'must_have_any_tags_from'",
        "Has two from 'must_have_all_tags_from' and none from 'must_have_any_tags_from'",
        "Has one from 'must_have_all_tags_from' and one from 'must_have_any_tags_from'",
    ],
    argvalues=[
        (
            {
                "tags": ["tag1", "tag2", "tag3"],
            },
            ["tag1", "tag2"],
            None,
            True,
        ),
        (
            {
                "tags": ["tag1"],
            },
            None,
            ["tag1", "tag2"],
            True,
        ),
        (
            {
                "tags": ["tag1", "tag2"],
            },
            None,
            ["tag1", "tag2"],
            True,
        ),
        (
            {
                "tags": ["tag1"],
            },
            None,
            ["tag1", "tag2"],
            True,
        ),
        (
            {
                "tags": [],
            },
            None,
            ["tag1", "tag2"],
            False,
        ),
        (
            {
                "tags": ["tag1", "tag2", "tag3"],
            },
            ["tag1", "tag2"],
            ["tag3", "tag4"],
            True,
        ),
        (
            {
                "tags": ["tag1", "tag3"],
            },
            ["tag1", "tag2"],
            ["tag3", "tag4"],
            False,
        ),
        (
            {
                "tags": ["tag1", "tag2"],
            },
            ["tag1", "tag2"],
            ["tag3", "tag4"],
            False,
        ),
    ],
)
def test_taggable_mixin_has_required_tags(
    data: dict,
    must_have_all_tags_from: list[str],
    must_have_any_tags_from: list[str],
    expected_return: bool,
):
    instance = ConcreteTaggableNode(data)
    assert (
        instance.has_required_tags(
            must_have_all_tags_from=must_have_all_tags_from,
            must_have_any_tag_from=must_have_any_tags_from,
        )
        is expected_return
    )
