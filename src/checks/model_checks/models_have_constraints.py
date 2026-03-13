"""Check if models have constraints."""

from typing import Collection

from utils.check_failure_messages import (
    object_missing_attribute_message,
    object_missing_values_from_set_message,
)
from utils.check_abc import ManifestCheck


class ModelsHaveConstraints(ManifestCheck):
    """Check if models have constraints.

    Attributes:
        check_name: name of the check
        additional_arguments: arguments required in addition to the global arguments
    """

    check_name: str = "models-have-constraints"
    additional_arguments = [
        "must_have_all_constraints_from",
        "must_have_any_constraint_from",
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
        self.failures: dict[str, set[str]] = {
            model.unique_id: {constraint.type for constraint in model.constraints}
            for model in self.manifest.in_scope_models
            if not model.has_required_constraints(
                must_have_all_constraints_from=self.args.must_have_all_constraints_from,
                must_have_any_constraint_from=self.args.must_have_any_constraint_from,
            )
        }

    @property
    def failure_message(self) -> str:
        """Compile a failure log message."""
        return object_missing_values_from_set_message(
            objects=self.failures,
            object_type="model",
            attribute_type="constraint",
            must_have_all_from=self.args.must_have_all_constraints_from,
            must_have_any_from=self.args.must_have_any_constraint_from,
        )


if __name__ == "__main__":
    ModelsHaveConstraints()
