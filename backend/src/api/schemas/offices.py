from uuid import UUID

from pydantic import BaseModel

from usecases.dto.office import (
    CreateOfficeDTO,
    OfficeFiltersDTO,
    OfficeResponseDTO,
    UpdateOfficeDTO,
)


class GetOfficesFilters(BaseModel):
    is_active: bool | None = None
    city: str | None = None
    limit: int = 100
    offset: int = 0

    def to_dto(self) -> OfficeFiltersDTO:
        return OfficeFiltersDTO(
            is_active=self.is_active,
            city=self.city,
            limit=self.limit,
            offset=self.offset,
        )


class CreateOfficeRequest(BaseModel):
    name: str
    city: str
    address: str

    def to_dto(self) -> CreateOfficeDTO:
        return CreateOfficeDTO(
            name=self.name,
            city=self.city,
            address=self.address,
        )


class UpdateOfficeRequest(BaseModel):
    name: str | None = None
    city: str | None = None
    address: str | None = None

    def to_dto(self, office_id: UUID) -> UpdateOfficeDTO:
        return UpdateOfficeDTO(
            id=office_id,
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
