from utils.manifest_object.node.node import ManifestNode


class ManifestSeed(ManifestNode):
    def filter_by_resource_type(self) -> bool:
        return self.data.get("resource_type") == "seed"
