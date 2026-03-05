from dataclasses import dataclass

from utils.manifest_object.node.model.constraint import Constraint


@dataclass(eq=True, frozen=True)
class ManifestSourceColumn:
    data: dict

    @property
    def name(self) -> str:
        return self.data["name"]

    @property
    def data_type(self) -> str:
        return self.data.get("data_type")

    @property
    def has_data_type(self) -> str:
        return self.data_type is not None

    @property
    def constraints(self) -> tuple[Constraint, ...]:
        return tuple(
            Constraint(constraint_data)
            for constraint_data in self.data.get("constraints", [])
        )

    @property
    def description(self) -> str:
        return self.data.get("description")

    @property
    def has_description(self) -> bool:
        return self.description is not None
