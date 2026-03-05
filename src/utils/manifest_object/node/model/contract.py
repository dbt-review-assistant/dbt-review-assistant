from dataclasses import dataclass


@dataclass(eq=True, frozen=True)
class Contract:
    data: dict

    @property
    def enforced(self) -> bool:
        return bool(self.data.get("enforced", False))
