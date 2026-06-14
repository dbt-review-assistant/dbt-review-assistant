"""Check if seeds have columns listed in the manifest."""

from utils.check_abc import STANDARD_SEED_ARGUMENTS, ManifestCheck
from utils.check_failure_messages import object_missing_attribute_message


class SeedsHaveColumns(ManifestCheck):
    """Check if seeds have columns listed in the manifest.

    Attributes:
        check_name: name of the check
        additional_arguments: arguments required in addition to the global arguments
    """

    check_name: str = "seeds-have-columns"
    additional_arguments = STANDARD_SEED_ARGUMENTS

    def perform_check(self) -> None:
        """Execute the check logic."""
        self.failures = {
            seed.unique_id for seed in self.manifest.in_scope_seeds if not seed.columns
        }

    @property
    def failure_message(self) -> str:
        """Compile a failure log message."""
        return object_missing_attribute_message(
            missing_attributes=self.failures,
            object_type="seed",
            attribute_type="column",
        )
