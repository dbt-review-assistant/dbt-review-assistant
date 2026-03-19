"""Classes representing generic tests from the manifest file."""

from utils.manifest_object.node.node import ManifestNode


class GenericTest(ManifestNode):
    """Represents a manifest generic test object."""

    @property
    def generic_test_name(self) -> str | None:
        """The name of the generic test.

        Note this is the generic name, not the name of a specific instance.
        """
        return self.data.get("test_metadata", {}).get("name")
