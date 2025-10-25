"""Check if models have constraints."""

from typing import Collection

from utils.check_failure_messages import object_missing_attribute_message
from checks.model_checks.models_have_contracts import model_has_contract_enforced
from utils.check_abc import ManifestCheck
from utils.artifact_data import get_models_from_manifest


def model_has_constraints(
    model: dict, required_constraints: None | Collection[str] = None
) -> bool:
    """Check if a model has constraints, or has all required constraints.

    If required_constraints is provided, then all additional constraints are ignored.

    Args:
        model: model dictionary from the dbt manifest.json
        required_constraints: Optional, all required constraints

    Returns:
        True if the model has constraints, or all required constraints
    """
    model_constraints = model.get("constraints", [])
    model_constraints += [
        constraint["type"]
        for column_data in model.get("columns", {}).values()
        for constraint in column_data.get("constraints", [])
    ]
    if required_constraints:
        return set(required_constraints).issubset(set(model_constraints))
    return bool(model_constraints)


class ModelsHaveConstraints(ManifestCheck):
    """Check if models have constraints.

    Attributes:
        check_name: name of the check
        additional_arguments: arguments required in addition to the global arguments
    """

    check_name: str = "models-have-constraints"
    additional_arguments = [
        "constraints",
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
            node["unique_id"]
            for node in get_models_from_manifest(
                manifest_dir=self.args.manifest_dir,
                filter_conditions=self.filter_conditions,
            )
            if not (
                model_has_contract_enforced(node)
                and model_has_constraints(node, self.args.constraints)
            )
        }

    @property
    def failure_message(self) -> str:
        """Compile a failure log message."""
        return object_missing_attribute_message(
            missing_attributes=self.failures,
            object_type="model",
            attribute_type="constraint",
            expected_values=self.args.constraints,
        )


if __name__ == "__main__":
    ModelsHaveConstraints()
