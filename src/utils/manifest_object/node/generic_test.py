from utils.manifest_object.node.node import ManifestNode


class GenericTest(ManifestNode):
    def filter_by_resource_type(self) -> bool:
        return self.data.get("resource_type") == "test"

    @property
    def generic_test_name(self) -> str:
        return self.data.get("test_metadata", {}).get("name")
