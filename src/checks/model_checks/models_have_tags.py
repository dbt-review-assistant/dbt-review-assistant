"""CHeck if models have a description."""

from utils.check_failure_messages import object_missing_attribute_message
from utils.check_abc import ManifestCheck
from utils.artifact_data import get_models_from_manifest


class ModelsHaveTags(ManifestCheck):
    """CHeck if models have tags.

    Attributes:
        check_name: name of the check
        additional_arguments: arguments required in addition to the global arguments
    """

    check_name: str = "models-have-tags"
    additional_arguments = [
        "require_tags",
        "include_materializations",
        "include_tags",
        "include_packages",
        "include_node_paths",
        "exclude_materializations",
        "exclude_tags",
        "exclude_packages",
        "exclude_node_paths",
    ]

    def perform_check(self) -> None:
        """Execute the check logic."""
        self.failures = {
            model["unique_id"]
            for model in get_models_from_manifest(
                manifest_dir=self.args.manifest_dir,
                filter_conditions=self.filter_conditions,
            )
            if not ((model.get("tags", []) + model.get("config", {}).get("tags", [])))
        }

    @property
    def failure_message(self) -> str:
        """Compile a failure log message."""
        return object_missing_attribute_message(
            missing_attributes=self.failures,
            object_type="model",
            attribute_type="description",
        )
