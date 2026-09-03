from uuid import UUID

from pydantic import BaseModel

from usecases.commands.offices.create_office import CreateOfficeCommand
from usecases.commands.offices.update_office import UpdateOfficeCommand
from usecases.dto.office import OfficeResponseDTO
from usecases.queries.offices.get_offices import GetOfficesQuery


class GetOfficesFilters(BaseModel):
    is_active: bool | None = None
    city: str | None = None
    limit: int = 100
    offset: int = 0

    def to_query(self) -> GetOfficesQuery:
        return GetOfficesQuery(
            is_active=self.is_active,
            city=self.city,
            limit=self.limit,
            offset=self.offset,
        )


class CreateOfficeRequest(BaseModel):
    name: str
    city: str
    address: str

    def to_command(self) -> CreateOfficeCommand:
        return CreateOfficeCommand(
            name=self.name,
            city=self.city,
            address=self.address,
        )


class UpdateOfficeRequest(BaseModel):
    name: str | None = None
    city: str | None = None
    address: str | None = None

    def to_command(self, office_id: UUID) -> UpdateOfficeCommand:
        return UpdateOfficeCommand(
            office_id=office_id,
            name=self.name,
            city=self.city,
            address=self.address,
        )


class OfficeResponse(BaseModel):
    id: UUID
    name: str
    city: str
    address: str
    image_url: str | None
    is_active: bool

    @classmethod
    def from_dto(cls, dto: OfficeResponseDTO) -> "OfficeResponse":
        return cls(
            id=dto.id,
            name=dto.name,
            city=dto.city,
            address=dto.address,
            image_url=dto.image_url,
            is_active=dto.is_active,
        )
