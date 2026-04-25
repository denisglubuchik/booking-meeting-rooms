from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True, kw_only=True)
class Office:
    id: UUID
    name: str
    city: str
    address: str
    is_active: bool = True

    def activate(self) -> None:
        self.is_active = True

    def deactivate(self) -> None:
        self.is_active = False

    def update(
        self,
        name: str | None = None,
        city: str | None = None,
        address: str | None = None,
    ) -> None:
        if name is not None:
            self.name = name
        if city is not None:
            self.city = city
        if address is not None:
            self.address = address
