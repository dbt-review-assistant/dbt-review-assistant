from enum import Enum


class Constraint:
    def __init__(self, data: dict):
        self.data = data

    @property
    def type(self) -> str:
        constraint_type = self.data.get("type")
        if ConstraintType(constraint_type):
            return self.data.get("type")
        valid_constraint_types = "\n".join(ConstraintType.__members__.values())
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
