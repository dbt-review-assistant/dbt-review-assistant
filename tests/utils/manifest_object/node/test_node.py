from pathlib import Path
from unittest.mock import PropertyMock, patch

import pytest

from utils.manifest_filter_conditions import ManifestFilterConditions
from utils.manifest_object.manifest_object import (
    ConfigurableMixin,
    HasPatchPathMixin,
    ManifestObject,
    TaggableMixin,
)
from utils.manifest_object.node.node import ManifestNode


class ConcreteManifestNode(ManifestNode):
    pass


class ConcreteTaggableNode(TaggableMixin, ManifestObject):
    pass


@pytest.mark.parametrize(
    argnames=[
        "data",
        "include_tags",
        "exclude_tags",
        "expected_return",
    ],
    ids=[
        "Explicitly included",
        "Not explicitly included",
        "Explicitly excluded",
        "Not explicitly excluded",
        "Explicitly included, with exclude condition",
        "Explicitly excluded, with include condition",
        "Both explicitly included and explicitly excluded - exclude should take precedence",
    ],
    argvalues=[
        (
            {
                "unique_id": "included-model",
                "tags": ["test_tag", "another_tag"],
            },
            ["test_tag"],
            None,
            True,
        ),
        (
            {
                "unique_id": "excluded-model",
                "tags": ["test_tag", "another_tag"],
            },
            ["different_tag"],
            None,
            False,
        ),
        (
            {
                "unique_id": "excluded-model",
                "tags": ["test_tag", "another_tag"],
            },
            None,
            ["test_tag"],
            False,
        ),
        (
            {
                "unique_id": "included-model",
                "tags": ["test_tag", "another_tag"],
            },
            None,
            ["different_tag"],
            True,
        ),
        (
            {
                "unique_id": "included-model",
                "tags": ["test_tag", "another_tag"],
            },
            ["test_tag"],
            ["different_tag"],
            True,
        ),
        (
            {
                "unique_id": "excluded-model",
                "tags": ["test_tag", "another_tag"],
            },
            ["different_tag"],
            ["another_tag"],
            False,
        ),
        (
            {
                "unique_id": "excluded-model",
                "tags": ["test_tag", "another_tag"],
            },
            ["test_tag"],
            ["another_tag"],
            False,
        ),
    ],
)
def test_taggable_mixin_filter_by_tags(
    data: dict,
    include_tags: list[str],
    exclude_tags: list[str],
    expected_return: bool,
):
    instance = ConcreteTaggableNode(
        data=data,
        filter_conditions=ManifestFilterConditions(
            _include_tags=include_tags,
            _exclude_tags=exclude_tags,
        ),
    )
    assert instance.filter_by_tags is expected_return


@pytest.mark.parametrize(
    argnames=[
        "parent_in_scope",
        "filter_by_tags",
        "expected_return",
    ],
    ids=[
        "All filters in scope",
        "No filters in scope",
        "Parent in scope, tags out of scope",
        "Parent out of scope, tags in scope",
    ],
    argvalues=[
        (True, True, True),
        (False, False, False),
        (True, False, False),
        (False, True, False),
    ],
)
def test_taggable_mixin_is_in_scope(
    parent_in_scope: bool,
    filter_by_tags: bool,
    expected_return: bool,
):
    with (
        patch.object(
            ManifestObject,
            "is_in_scope",
            new_callable=PropertyMock(return_value=parent_in_scope),
        ),
        patch.object(
            ConcreteTaggableNode,
            "filter_by_tags",
            new_callable=PropertyMock(return_value=filter_by_tags),
        ),
    ):
        instance = ConcreteTaggableNode({}, ManifestFilterConditions())
        assert instance.is_in_scope is expected_return


class ConcreteConfigurableNode(ConfigurableMixin, ManifestObject):
    pass


@pytest.mark.parametrize(
    argnames=["data", "expected_return"],
    ids=[
        "Has config",
        "No config",
        "Config is None",
    ],
    argvalues=[
        (
            {"config": {"enabled": True}},
            {"enabled": True},
        ),
        ({}, {}),
        ({"config": None}, {}),
    ],
)
def test_configurable_mixin_config(data: dict, expected_return: bool):
    instance = ConcreteConfigurableNode(data, ManifestFilterConditions())
    assert instance.config == expected_return


@pytest.mark.parametrize(
    argnames=["data", "expected_return"],
    ids=[
        "Enabled",
        "Disabled",
    ],
    argvalues=[
        ({"config": {"enabled": True}}, True),
        ({"config": {"enabled": False}}, False),
    ],
)
def test_configurable_mixin_enabled(data: dict, expected_return: bool):
    instance = ConcreteConfigurableNode(data, ManifestFilterConditions())
    assert instance.enabled == expected_return


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
    instance = ConcreteHasPatchPathNode(data, ManifestFilterConditions())
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
    instance = ConcreteTaggableNode(data, ManifestFilterConditions())
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
    instance = ConcreteTaggableNode(data, ManifestFilterConditions())
    assert (
        instance.has_required_tags(
            must_have_all_tags_from=must_have_all_tags_from,
            must_have_any_tag_from=must_have_any_tags_from,
        )
        is expected_return
    )
