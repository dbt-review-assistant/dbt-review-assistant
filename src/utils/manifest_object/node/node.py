"""Classes representing nodes from the manifest file."""

from abc import ABC

from utils.manifest_object.manifest_object import (
    HasPatchPathMixin,
    ManifestObject,
    TaggableMixin,
)


class ManifestNode(TaggableMixin, ManifestObject, HasPatchPathMixin, ABC):
    """Represents a node from the manifest file."""

    pass


class ManifestAnalysis(ManifestNode):
    """Represents an analysis from the manifest file."""

    pass


class ManifestFunction(ManifestNode):
    """Represents a function from the manifest file."""

    pass


class ManifestHookNode(ManifestNode):
    """Represents a hook from the manifest file."""

    pass


class ManifestSeed(ManifestNode):
    """Represents a seed from the manifest file."""

    pass


class SingularTest(ManifestNode):
    """Represents a singular test from the manifest file."""

    pass


class ManifestSnapshot(ManifestNode):
    """Represents a snapshot from the manifest file."""

    pass


class ManifestSqlOperation(ManifestNode):
    """Represents a sql operation from the manifest file."""

    pass
