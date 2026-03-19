from abc import ABC

from utils.manifest_object.manifest_object import (
    ManifestObject,
    TaggableMixin,
    HasPatchPathMixin,
)


class ManifestNode(TaggableMixin, ManifestObject, HasPatchPathMixin, ABC):
    pass


class ManifestAnalysis(ManifestNode):
    pass


class ManifestFunction(ManifestNode):
    pass


class ManifestHookNode(ManifestNode):
    pass


class ManifestSeed(ManifestNode):
    pass


class SingularTest(ManifestNode):
    pass


class ManifestSnapshot(ManifestNode):
    pass


class ManifestSqlOperation(ManifestNode):
    pass
