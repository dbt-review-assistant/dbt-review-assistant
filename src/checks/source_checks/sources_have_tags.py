"""Check if sources have tags."""

from utils.check_abc import STANDARD_SOURCE_ARGUMENTS, ManifestCheck
from utils.check_failure_messages import object_missing_values_from_set_message


class SourcesHaveTags(ManifestCheck):
    """Check if sources have tags.

    Attributes:
        check_name: name of the check
        additional_arguments: arguments required in addition to the global arguments
    """

    check_name: str = "sources-have-tags"
    additional_arguments = STANDARD_SOURCE_ARGUMENTS + [
        "must_have_all_tags_from",
        "must_have_any_tag_from",
    ]

    def perform_check(self) -> None:
        """Execute the check logic."""
        self.failures: dict[str, set[str]] = {
            source.unique_id: source.tags
            for source in self.manifest.in_scope_sources
            if not source.has_required_tags(
                must_have_any_tag_from=self.args.must_have_any_tag_from,
                must_have_all_tags_from=self.args.must_have_all_tags_from,
            )
        }

    @property
    def failure_message(self) -> str:
        """Compile a failure log message."""
        return object_missing_values_from_set_message(
            objects=self.failures,
            object_type="source",
            attribute_type="tag",
            must_have_all_from=self.args.must_have_all_tags_from,
            must_have_any_from=self.args.must_have_any_tag_from,
        )
