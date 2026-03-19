"""Classes representing contracts for objects in the manifest file."""

from dataclasses import dataclass


@dataclass(eq=True, frozen=True)
class Contract:
    """Represents a contract for an object from manifest file.

    Attributes:
        data: dictionary of data for the contract from the manifest file.
    """

    data: dict

    @property
    def enforced(self) -> bool:
        """Whether the contract is enforced for this object instance."""
        return bool(self.data.get("enforced", False))
