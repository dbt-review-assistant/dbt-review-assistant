"""Classes representing constraints on objects from the manifest file."""

from dataclasses import dataclass
from enum import Enum


@dataclass(eq=True, frozen=True)
class Constraint:
    """Represents a constraint on the manifest file.

    Attributes:
        data: dictionary of constraint data from the manifest fiel.
    """

    data: dict

    @property
    def type(self) -> str:
        """The type of the constraint."""
        constraint_type = self.data["type"]
        try:
            ConstraintType(constraint_type)
            return constraint_type
        except ValueError:
            valid_constraint_types = "\n".join(
                constraint.value for constraint in ConstraintType.__members__.values()
            )
            raise ValueError(
                f"Unknown constraint type: {constraint_type}\nValid constraints: {valid_constraint_types}"
            )


class ConstraintType(Enum):
    """Enum for all valid constraint types."""

    CHECK = "check"
    NOT_NULL = "not_null"
    UNIQUE = "unique"
    PRIMARY_KEY = "primary_key"
    FOREIGN_KEY = "foreign_key"
    CUSTOM = "custom"
