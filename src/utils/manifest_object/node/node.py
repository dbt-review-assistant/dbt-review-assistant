from abc import ABC
from pathlib import Path
from typing import Any

from utils.manifest_object.manifest_object import ManifestObject, TaggableMixin, HasPatchPathMixin


class ManifestNode(TaggableMixin, ManifestObject, HasPatchPathMixin, ABC):
    @property
    def config(self) -> dict[str, Any]:
        return self.data.get("config", {}) or {}

    @property
    def enabled(self) -> bool:
        return self.config.get("enabled", True)

    @property
    def patch_path(self) -> Path | None:
        return Path(self.data.get("patch_path")) if self.data.get("patch_path") else None


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
