from utils.manifest_object.node.node import ManifestNode


class GenericTest(ManifestNode):
    @property
    def generic_test_name(self) -> str | None:
        return self.data.get("test_metadata", {}).get("name")
