"""Check if macro arguments have data types."""

from utils.check_failure_messages import object_missing_attribute_message
from utils.check_abc import ManifestCheck
from utils.artifact_data import get_macros_from_manifest


class MacroArgumentsHaveTypes(ManifestCheck):
    """Check if macro arguments have data types.

    Attributes:
        check_name: name of the check
        additional_arguments: arguments required in addition to the global arguments
    """

    check_name: str = "macro-arguments-have-types"
    additional_arguments = [
        "include_packages",
        "include_tags",
        "exclude_packages",
        "exclude_tags",
    ]

    def perform_check(self) -> None:
        """Execute the check logic."""
        macros = get_macros_from_manifest(
            manifest_dir=self.args.manifest_dir,
            filter_conditions=self.filter_conditions,
        )
        self.failures = {
            f"{node['unique_id']}.{argument['name']}"
            for node in macros
            for argument in node.get("arguments", [])
            if not argument.get("type", False)
        }

    @property
    def failure_message(self) -> str:
        """Compile a failure log message."""
        return object_missing_attribute_message(
            missing_attributes=self.failures,
            object_type="macro argument",
            attribute_type="type",
        )


if __name__ == "__main__":
    MacroArgumentsHaveTypes()
