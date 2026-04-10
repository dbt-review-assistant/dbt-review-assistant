"""Methods for finding parents and children of manifest objects."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from utils.artifact_data import Manifest


def get_direct_children(unique_id: str, manifest: "Manifest") -> set[str]:
    """Unique IDs of the direct children of this object.

    Arguments:
        unique_id: Unique ID of this object.
        manifest: Manifest instance to search.

    Returns:
        set of unique IDs of the direct children of this object.
    """
    return set(manifest.child_map.get(unique_id, []))


def get_direct_parents(unique_id: str, manifest: "Manifest") -> set[str]:
    """Unique IDs of the direct parents of this object.

    Arguments:
        unique_id: Unique ID of this object.
        manifest: Manifest instance to search.

    Returns:
        set of unique IDs of the direct parents of this object.
    """
    return set(manifest.parent_map.get(unique_id, []))


def get_all_parents(
    unique_id: str,
    manifest: "Manifest",
    include_indirect: bool = True,
) -> set[str]:
    """Unique IDs of the all parents of this object.

    Arguments:
        unique_id: Unique ID of this object.
        manifest: Manifest instance to search.
        include_indirect: Whether to include indirect parents. Optional, defaults to True.

    Returns:
        a set of unique IDs of all parents of this object.
    """
    all_parents = set()
    direct_parents = get_direct_parents(unique_id, manifest)
    all_parents.update(direct_parents)
    if include_indirect:
        for parent in direct_parents:
            all_parents.update(
                get_all_parents(
                    unique_id=parent,
                    manifest=manifest,
                    include_indirect=True,
                )
            )
    return all_parents


def get_all_children(
    unique_id: str,
    manifest: "Manifest",
    include_indirect: bool = True,
) -> set[str]:
    """Unique IDs of the all children of this object.

    Arguments:
        unique_id: Unique ID of this object.
        manifest: Manifest instance to search.
        include_indirect: Whether to include indirect children. Optional, defaults to True.

    Returns:
        a set of unique IDs of all children of this object.
    """
    all_children = set()
    direct_children = get_direct_children(unique_id, manifest)
    all_children.update(direct_children)
    if include_indirect:
        for parent in direct_children:
            all_children.update(
                get_all_children(
                    unique_id=parent,
                    manifest=manifest,
                    include_indirect=True,
                )
            )
    return all_children
