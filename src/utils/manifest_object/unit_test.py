"""Classes representing unit tests from the manifest file."""

from utils.manifest_object.manifest_object import (
    ManifestObject,
    TaggableMixin,
    HasPatchPathMixin,
)


class UnitTest(ManifestObject, TaggableMixin, HasPatchPathMixin):
    """Represents unit tests from the manifest file."""

    @property
    def original_filepath(self) -> str:
        """The original filepath of the unit test."""
        return self.data["original_filepath"]
