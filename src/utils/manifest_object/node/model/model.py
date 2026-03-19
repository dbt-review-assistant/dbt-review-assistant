"""Classes representing models from the manifest file."""

from typing import TYPE_CHECKING, Collection

from utils.manifest_object.manifest_object import DataTestableMixin, ManifestColumn
from utils.manifest_object.node.model.constraint import Constraint
from utils.manifest_object.node.model.contract import Contract
from utils.manifest_object.node.node import ManifestNode

if TYPE_CHECKING:
    from utils.artifact_data import Manifest


class ManifestModel(ManifestNode, DataTestableMixin):
    """Represents a model from the manifest file."""

    @property
    def columns(self) -> dict[str, ManifestColumn]:
        """The model's columns.

        Returns:
            a dictionary mapping column unique IDs to ManifestColumn instances.
        """
        return {
            f"{self.unique_id}.{column_name}": ManifestColumn(column_data)
            for column_name, column_data in self.data.get("columns", {}).items()
        }

    @property
    def constraints(self) -> tuple[Constraint, ...]:
        """The model's constraints.

        Returns:
            a tuple of Constraint instances.
        """
        return tuple(
            Constraint(constraint_data)
            for constraint_data in self.data.get("constraints", [])
        )

    @property
    def contract(self) -> Contract | None:
        """The model's contract.

        Returns:
            a Contract instance.
        """
        contract_data = self.config.get("contract", {})
        if contract_data:
            return Contract(contract_data)
        return None

    @property
    def materialized(self) -> str | None:
        """The model's configured materialization type."""
        return self.config.get("materialized")

    @property
    def has_contract(self) -> bool:
        """Whether the model has an enforced contract.

        Note - will always return False for ephemeral models
        """
        return (
            self.contract is not None
            and self.contract.enforced
            and self.materialized != "ephemeral"
        )

    @property
    def filter_by_materialization_type(self) -> bool:
        """Whether the model is considered in-scope, based on materialization type."""
        return (
            self.filter_conditions.include_materializations is None
            or self.materialized in self.filter_conditions.include_materializations
        ) and (
            self.filter_conditions.exclude_materializations is None
            or self.materialized not in self.filter_conditions.exclude_materializations
        )

    def has_required_constraints(
        self,
        must_have_all_constraints_from: Collection[str] | None = None,
        must_have_any_constraint_from: Collection[str] | None = None,
    ) -> bool:
        """Whether the model has required constraints.

        Args:
            must_have_all_constraints_from: Collection of constraint types the model must have. Optional, defaults to None.
            must_have_any_constraint_from: Collection of constraint types of which the model must have at least one. Optional, defaults to None.

        Returns:
            True if the model has required constraints, False otherwise.
        """
        constraints = {constraint.type for constraint in self.constraints}
        constraints.update(
            {
                constraint.type
                for column in self.columns.values()
                for constraint in column.constraints
            }
        )
        has_required_constraints = bool(constraints)
        if (
            must_have_all_constraints_from is None
            and must_have_any_constraint_from is None
        ):
            return has_required_constraints
        if must_have_all_constraints_from is not None:
            has_required_constraints = bool(
                set(must_have_all_constraints_from).issubset(constraints)
            )
        if must_have_any_constraint_from is not None:
            has_required_constraints = (
                bool(set(must_have_any_constraint_from).intersection(constraints))
                and has_required_constraints
            )
        return has_required_constraints

    def has_unit_tests(self, manifest: "Manifest") -> bool:
        """Whether the model has unit tests.

        Args:
            manifest: Manifest instance to look up unit tests from

        Returns:
            True if model has unit tests, False otherwise.
        """
        for child_id in manifest.child_map.get(self.unique_id, []):
            unit_test = manifest.unit_tests.get(child_id)
            if unit_test:
                return True
        return False
