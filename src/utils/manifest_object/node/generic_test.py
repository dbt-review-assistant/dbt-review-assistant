"""Classes representing generic tests from the manifest file."""

from utils.manifest_object.node.node import ManifestNode


class GenericTest(ManifestNode):
    """Represents a manifest generic test object."""

    @property
    def name(self) -> str:
        """The name of the generic test.

        Note - this is the generic name, not the name of a specific instance.
        For the name of the specific test instance use
        GenericTest.test_instance_name.
        """
        name = self.data.get("test_metadata", {}).get("name")
        if not name:
            raise AttributeError(f"{self.unique_id} has no generic test name.")
        return name

    @property
    def instance_name(self) -> str:
        """The name of the specific test instance.

        Note - for the name of the generic test use GenericTest.name.
        """
        return self.data["name"]
