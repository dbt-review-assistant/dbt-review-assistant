"""Check if models have a description."""

from utils.check_abc import STANDARD_MODEL_ARGUMENTS, ManifestCheck
from utils.check_failure_messages import (
    object_missing_values_from_set_message,
)


class ModelsHaveTags(ManifestCheck):
    """Check if models have tags.

    Attributes:
        check_name: name of the check
        additional_arguments: arguments required in addition to the global arguments
    """

    check_name: str = "models-have-tags"
    additional_arguments = STANDARD_MODEL_ARGUMENTS + [
        "must_have_all_tags_from",
        "must_have_any_tag_from",
    ]

    def perform_check(self) -> None:
        """Execute the check logic."""
        self.failures: dict[str, set[str]] = {
            model.unique_id: model.tags
            for model in self.manifest.in_scope_models
            if not model.has_required_tags(
                must_have_any_tag_from=self.args.must_have_any_tag_from,
                must_have_all_tags_from=self.args.must_have_all_tags_from,
            )
        }

    @property
    def failure_message(self) -> str:
        """Compile a failure log message."""
        return object_missing_values_from_set_message(
            objects=self.failures,
            object_type="model",
            attribute_type="tag",
            must_have_all_from=self.args.must_have_all_tags_from,
            must_have_any_from=self.args.must_have_any_tag_from,
        )
