"""Check if models have contracts enforced."""

from utils.check_failure_messages import object_missing_attribute_message
from utils.check_abc import ManifestCheck


def model_has_contract_enforced(model: dict) -> bool:
    """Check if a model has a contract enforced.

    Args:
        model: model dictionary from the dbt manifest.json

    Returns:
        True if the model has an enforced contract
    """
    config = model.get("config", {})
    contract = config.get("contract", {})
    enforced = contract is not None and contract.get("enforced", False)
    return enforced


class ModelsHaveContracts(ManifestCheck):
    """Check if models have contracts enforced.

    Attributes:
        check_name: name of the check
        additional_arguments: arguments required in addition to the global arguments
    """

    check_name: str = "models-have-contracts"
    additional_arguments = [
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
            model.unique_id
            for model in self.manifest.in_scope_models
            if not model.has_contract
        }

    @property
    def failure_message(self) -> str:
        """Compile a failure log message."""
        return object_missing_attribute_message(
            missing_attributes=self.failures,
            object_type="model",
            attribute_type="contract",
        )


if __name__ == "__main__":
    ModelsHaveContracts()
