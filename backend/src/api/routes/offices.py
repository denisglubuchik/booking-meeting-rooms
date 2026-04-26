from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Query

from api.schemas.offices import (
    CreateOfficeRequest,
    GetOfficesFilters,
    OfficeResponse,
    UpdateOfficeRequest,
)
from usecases.offices.activate_office import ActivateOfficeUseCase
from usecases.offices.create_office import CreateOfficeUseCase
from usecases.offices.deactivate_office import DeactivateOfficeUseCase
from usecases.offices.get_office_details import GetOfficeDetailsUseCase
from usecases.offices.get_offices import GetOfficesUseCase
from usecases.offices.update_office import UpdateOfficeUseCase

router = APIRouter(tags=["offices"], route_class=DishkaRoute)


@router.get("/")
async def get_offices(
    get_offices_uc: FromDishka[GetOfficesUseCase],
    filters: Annotated[GetOfficesFilters, Query()],
) -> list[OfficeResponse]:
    offices = await get_offices_uc.execute(filters.to_dto())
    return [OfficeResponse.from_dto(office) for office in offices]


@router.get("/{office_id}")
async def get_office(
    office_id: UUID,
    get_office_uc: FromDishka[GetOfficeDetailsUseCase],
) -> OfficeResponse:
    office = await get_office_uc.execute(office_id)
    return OfficeResponse.from_dto(office)


@router.post("/")
async def create_office(
    payload: CreateOfficeRequest,
    create_office_uc: FromDishka[CreateOfficeUseCase],
) -> OfficeResponse:
    office = await create_office_uc.execute(payload.to_dto())
    return OfficeResponse.from_dto(office)


@router.patch("/{office_id}")
async def update_office(
    office_id: UUID,
    payload: UpdateOfficeRequest,
    update_office_uc: FromDishka[UpdateOfficeUseCase],
) -> OfficeResponse:
    office = await update_office_uc.execute(payload.to_dto(office_id))
    return OfficeResponse.from_dto(office)


@router.post("/{office_id}/activate")
async def activate_office(
    office_id: UUID,
    activate_office_uc: FromDishka[ActivateOfficeUseCase],
) -> OfficeResponse:
    office = await activate_office_uc.execute(office_id)
    return OfficeResponse.from_dto(office)


@router.post("/{office_id}/deactivate")
async def deactivate_office(
    office_id: UUID,
    deactivate_office_uc: FromDishka[DeactivateOfficeUseCase],
) -> OfficeResponse:
    office = await deactivate_office_uc.execute(office_id)
    return OfficeResponse.from_dto(office)
