import logging
from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, File, Query, UploadFile

from api.dependencies.auth import AdminUserDep, CurrentUserDep
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
from usecases.offices.image_ops import (
    DeleteOfficeImageUseCase,
    UploadOfficeImageUseCase,
)
from usecases.offices.update_office import UpdateOfficeUseCase

router = APIRouter(tags=["offices"], route_class=DishkaRoute)
logger = logging.getLogger("api.routes.offices")


@router.get("/")
async def get_offices(
    get_offices_uc: FromDishka[GetOfficesUseCase],
    filters: Annotated[GetOfficesFilters, Query()],
    _: CurrentUserDep,
) -> list[OfficeResponse]:
    logger.info("get_offices_started limit=%s offset=%s", filters.limit, filters.offset)
    offices = await get_offices_uc.execute(filters.to_dto())
    logger.info("get_offices_finished count=%s", len(offices))
    return [OfficeResponse.from_dto(office) for office in offices]


@router.get("/{office_id}")
async def get_office(
    office_id: UUID,
    get_office_uc: FromDishka[GetOfficeDetailsUseCase],
    _: CurrentUserDep,
) -> OfficeResponse:
    logger.info("get_office_started office_id=%s", office_id)
    office = await get_office_uc.execute(office_id)
    logger.info("get_office_finished office_id=%s", office.id)
    return OfficeResponse.from_dto(office)


@router.post("/")
async def create_office(
    payload: CreateOfficeRequest,
    create_office_uc: FromDishka[CreateOfficeUseCase],
    _: AdminUserDep,
) -> OfficeResponse:
    logger.info("create_office_started name=%s city=%s", payload.name, payload.city)
    office = await create_office_uc.execute(payload.to_dto())
    logger.info("create_office_finished office_id=%s", office.id)
    return OfficeResponse.from_dto(office)


@router.patch("/{office_id}")
async def update_office(
    office_id: UUID,
    payload: UpdateOfficeRequest,
    update_office_uc: FromDishka[UpdateOfficeUseCase],
    _: AdminUserDep,
) -> OfficeResponse:
    logger.info("update_office_started office_id=%s", office_id)
    office = await update_office_uc.execute(payload.to_dto(office_id))
    logger.info("update_office_finished office_id=%s", office.id)
    return OfficeResponse.from_dto(office)


@router.post("/{office_id}/activate")
async def activate_office(
    office_id: UUID,
    activate_office_uc: FromDishka[ActivateOfficeUseCase],
    _: AdminUserDep,
) -> OfficeResponse:
    logger.info("activate_office_started office_id=%s", office_id)
    office = await activate_office_uc.execute(office_id)
    logger.info("activate_office_finished office_id=%s", office.id)
    return OfficeResponse.from_dto(office)


@router.post("/{office_id}/deactivate")
async def deactivate_office(
    office_id: UUID,
    deactivate_office_uc: FromDishka[DeactivateOfficeUseCase],
    _: AdminUserDep,
) -> OfficeResponse:
    logger.info("deactivate_office_started office_id=%s", office_id)
    office = await deactivate_office_uc.execute(office_id)
    logger.info("deactivate_office_finished office_id=%s", office.id)
    return OfficeResponse.from_dto(office)


@router.post("/{office_id}/image", status_code=204)
async def upload_office_image(
    office_id: UUID,
    image: Annotated[UploadFile, File()],
    upload_image_uc: FromDishka[UploadOfficeImageUseCase],
    _: AdminUserDep,
) -> None:
    content_type = image.content_type or ""
    data = await image.read()
    logger.info(
        "upload_office_image_started office_id=%s content_type=%s size_bytes=%s",
        office_id,
        content_type,
        len(data),
    )
    await upload_image_uc.execute(
        office_id,
        content_type=content_type,
        data=data,
    )
    logger.info("upload_office_image_finished office_id=%s", office_id)


@router.delete("/{office_id}/image", status_code=204)
async def delete_office_image(
    office_id: UUID,
    delete_image_uc: FromDishka[DeleteOfficeImageUseCase],
    _: AdminUserDep,
) -> None:
    logger.info("delete_office_image_started office_id=%s", office_id)
    await delete_image_uc.execute(office_id)
    logger.info("delete_office_image_finished office_id=%s", office_id)
