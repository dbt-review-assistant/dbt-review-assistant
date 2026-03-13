from typing import TYPE_CHECKING, Collection

from utils.manifest_object.node.model.column import ManifestModelColumn
from utils.manifest_object.node.model.constraint import Constraint
from utils.manifest_object.node.model.contract import Contract
from utils.manifest_object.node.node import ManifestNode

if TYPE_CHECKING:
    from utils.artifact_data import Manifest


class ManifestModel(ManifestNode):
    @property
    def columns(self) -> dict[str, ManifestModelColumn]:
        return {
            f"{self.unique_id}.{column_name}": ManifestModelColumn(column_data)
            for column_name, column_data in self.data.get("columns", {}).items()
        }

    @property
    def constraints(self) -> tuple[Constraint, ...]:
        return tuple(
            Constraint(constraint_data)
            for constraint_data in self.data.get("constraints", [])
        )

    @property
    def contract(self) -> Contract | None:
        contract_data = self.config.get("contract", {})
        if contract_data:
            return Contract(contract_data)
        return None

    @property
    def materialized(self) -> str:
        return self.config.get("materialized")

    @property
    def has_contract(self) -> bool:
        return (
            self.contract is not None
            and self.contract.enforced
            and self.materialized != "ephemeral"
        )

    @property
    def filter_by_materialization_type(self) -> bool:
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
        for child_id in manifest.child_map.get(self.unique_id, []):
            unit_test = manifest.unit_tests.get(child_id)
            if unit_test:
                return True
        return False

    def get_data_tests(self, manifest: "Manifest") -> set[str]:
        generic_tests = {
            test.generic_test_name
            for test in map(
                manifest.generic_tests.get, manifest.child_map.get(self.unique_id, [])
            )
            if test
        }
        singular_tests = {
            test.unique_id
            for test in map(
                manifest.singular_tests.get, manifest.child_map.get(self.unique_id, [])
            )
            if test
        }
        return generic_tests.union(singular_tests)

    def has_required_data_tests(
        self,
        manifest: "Manifest",
        must_have_all_data_tests_from,
        must_have_any_data_test_from,
    ) -> bool:
        data_tests = self.get_data_tests(manifest)
        has_required_data_tests = bool(data_tests)
        if (
            must_have_all_data_tests_from is None
            and must_have_any_data_test_from is None
        ):
            return has_required_data_tests
        if must_have_all_data_tests_from is not None:
            has_required_data_tests = bool(
                set(must_have_all_data_tests_from).issubset(data_tests)
            )
        if must_have_any_data_test_from is not None:
            has_required_data_tests = (
                bool(set(must_have_any_data_test_from).intersection(data_tests))
                and has_required_data_tests
            )
        return has_required_data_tests
