from typing import Any

from utils.manifest_object.manifest_object import ManifestObject, TaggableMixin, HasPatchPathMixin


class UnitTest(ManifestObject, TaggableMixin, HasPatchPathMixin):
    @property
    def original_filepath(self) -> str:
        return self.data["original_filepath"]
