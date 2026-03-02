from typing import TYPE_CHECKING

from utils.manifest_object.node.model.column import ManifestModelColumn
from utils.manifest_object.node.model.constraint import Constraint
from utils.manifest_object.node.node import ManifestNode

if TYPE_CHECKING:
    from utils.artifact_data import Manifest


class Contract:
    def __init__(self, data: dict):
        self.data = data

    @property
    def enforced(self) -> bool:
        return self.data.get("enforced", False)


class ModelLevelConstraint(Constraint):
    pass


class ManifestModel(ManifestNode):
    @property
    def columns(self) -> dict[str, ManifestModelColumn]:
        return {
            f"{self.unique_id}.{column_name}": ManifestModelColumn(column_data)
            for column_name, column_data in self.data.get("columns", {}).items()
        }

    @property
    def constraints(self) -> tuple[ModelLevelConstraint, ...]:
        return tuple(
            ModelLevelConstraint(constraint_data)
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

    def filter_by_resource_type(self) -> bool:
        return self.data.get("resource_type") == "model"

    def filter_by_materialization_type(self) -> bool:
        return (
            self.filter_conditions.include_materializations is None
            or self.materialized in self.filter_conditions.include_materializations
        ) and (
            self.filter_conditions.exclude_materializations is None
            or self.materialized not in self.filter_conditions.exclude_materializations
        )

    @property
    def has_contract(self) -> bool:
        return (
            self.contract is not None
            and self.contract.enforced
            and self.materialized != "ephemeral"
        )

    def has_required_constraints(
        self, must_have_all_constraints_from=None, must_have_any_constraint_from=None
    ) -> bool:
        constraints = {constraint.type for constraint in self.constraints}
        constraints.update(
            {
                constraint.type
                for column in self.columns.values()
                for constraint in column.constraints
            }
        )
        return any(
            [
                # No specific constraints required
                (
                    not (
                        must_have_all_constraints_from or must_have_any_constraint_from
                    )
                    and not constraints
                ),
                # Full set of constraints required
                (
                    must_have_all_constraints_from
                    and not set(must_have_all_constraints_from).issubset(constraints)
                ),
                # At least one constraint from set required
                (
                    must_have_any_constraint_from
                    and not set(must_have_any_constraint_from).intersection(constraints)
                ),
            ]
        )

    def has_required_tags(
        self, must_have_all_tags_from=None, must_have_any_tag_from=None
    ) -> bool:
        return not any(
            [
                # No specific tags required
                (
                    not (must_have_all_tags_from or must_have_any_tag_from)
                    and not self.tags
                ),
                # Full set of tags required
                (
                    must_have_all_tags_from
                    and not set(must_have_all_tags_from).issubset(self.tags)
                ),
                # At least one tag from set required
                (
                    must_have_any_tag_from
                    and not set(must_have_any_tag_from).intersection(self.tags)
                ),
            ]
        )

    def has_unit_tests(self, manifest: "Manifest") -> bool:
        for child_id in manifest.child_map.get(self.unique_id, []):
            unit_test = manifest.unit_tests.get(child_id)
            if unit_test:
                return True
        return False

    def get_data_tests(self, manifest: "Manifest") -> set[str]:
        # TODO - find singular tests here too
        return {
            test.generic_test_name
            for test in map(
                manifest.generic_tests.get, manifest.child_map.get(self.unique_id, [])
            )
            if test
        }

    @staticmethod
    def has_required_data_tests(
        data_tests: set[str],
        must_have_all_data_tests_from,
        must_have_any_data_test_from,
    ) -> bool:
        return not any(
            [
                # No specific data_tests required
                # TODO - accept singular tests here too
                (
                    not (must_have_all_data_tests_from or must_have_any_data_test_from)
                    and not data_tests
                ),
                # Full set of data_tests required
                (
                    must_have_all_data_tests_from
                    and not set(must_have_all_data_tests_from).issubset(data_tests)
                ),
                # At least one data_test from set required
                (
                    must_have_any_data_test_from
                    and not set(must_have_any_data_test_from).intersection(data_tests)
                ),
            ]
        )
