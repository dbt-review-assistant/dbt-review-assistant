from dataclasses import dataclass
from enum import Enum


@dataclass(eq=True, frozen=True)
class Constraint:
    data: dict

    @property
    def type(self) -> str:
        constraint_type = self.data["type"]
        try:
            ConstraintType(constraint_type)
            return constraint_type
        except ValueError:
            valid_constraint_types = "\n".join(constraint.value for constraint in ConstraintType.__members__.values())
            raise ValueError(
                f"Unknown constraint type: {constraint_type}\nValid constraints: {valid_constraint_types}"
            )


class ConstraintType(Enum):
    CHECK = "check"
    NOT_NULL = "not_null"
    UNIQUE = "unique"
    PRIMARY_KEY = "primary_key"
    FOREIGN_KEY = "foreign_key"
    CUSTOM = "custom"
