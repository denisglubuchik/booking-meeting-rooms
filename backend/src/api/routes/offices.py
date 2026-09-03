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
from usecases.commands.offices.activate_office import (
    ActivateOfficeCommand,
    ActivateOfficeCommandHandler,
)
from usecases.commands.offices.create_office import CreateOfficeCommandHandler
from usecases.commands.offices.deactivate_office import (
    DeactivateOfficeCommand,
    DeactivateOfficeCommandHandler,
)
from usecases.commands.offices.image_ops import (
    DeleteOfficeImageCommand,
    DeleteOfficeImageCommandHandler,
    UploadOfficeImageCommand,
    UploadOfficeImageCommandHandler,
)
from usecases.commands.offices.update_office import (
    UpdateOfficeCommandHandler,
)
from usecases.queries.offices.get_office_details import (
    GetOfficeDetailsQuery,
    GetOfficeDetailsQueryHandler,
)
from usecases.queries.offices.get_offices import GetOfficesQueryHandler

router = APIRouter(tags=["offices"], route_class=DishkaRoute)
logger = logging.getLogger("api.routes.offices")


@router.get("/")
async def get_offices(
    handler: FromDishka[GetOfficesQueryHandler],
    filters: Annotated[GetOfficesFilters, Query()],
    _: CurrentUserDep,
) -> list[OfficeResponse]:
    logger.info(
        "get_offices_started limit=%s offset=%s",
        filters.limit,
        filters.offset,
    )
    offices = await handler.handle(filters.to_query())
    logger.info("get_offices_finished count=%s", len(offices))
    return [OfficeResponse.from_dto(office) for office in offices]


@router.get("/{office_id}")
async def get_office(
    office_id: UUID,
    handler: FromDishka[GetOfficeDetailsQueryHandler],
    _: CurrentUserDep,
) -> OfficeResponse:
    logger.info("get_office_started office_id=%s", office_id)
    office = await handler.handle(GetOfficeDetailsQuery(office_id=office_id))
    logger.info("get_office_finished office_id=%s", office.id)
    return OfficeResponse.from_dto(office)


@router.post("/")
async def create_office(
    payload: CreateOfficeRequest,
    handler: FromDishka[CreateOfficeCommandHandler],
    _: AdminUserDep,
) -> OfficeResponse:
    logger.info(
        "create_office_started name=%s city=%s",
        payload.name,
        payload.city,
    )
    office = await handler.handle(payload.to_command())
    logger.info("create_office_finished office_id=%s", office.id)
    return OfficeResponse.from_dto(office)


@router.patch("/{office_id}")
async def update_office(
    office_id: UUID,
    payload: UpdateOfficeRequest,
    handler: FromDishka[UpdateOfficeCommandHandler],
    _: AdminUserDep,
) -> OfficeResponse:
    logger.info("update_office_started office_id=%s", office_id)
    office = await handler.handle(payload.to_command(office_id))
    logger.info("update_office_finished office_id=%s", office.id)
    return OfficeResponse.from_dto(office)


@router.post("/{office_id}/activate")
async def activate_office(
    office_id: UUID,
    handler: FromDishka[ActivateOfficeCommandHandler],
    _: AdminUserDep,
) -> OfficeResponse:
    logger.info("activate_office_started office_id=%s", office_id)
    office = await handler.handle(ActivateOfficeCommand(office_id=office_id))
    logger.info("activate_office_finished office_id=%s", office.id)
    return OfficeResponse.from_dto(office)


@router.post("/{office_id}/deactivate")
async def deactivate_office(
    office_id: UUID,
    handler: FromDishka[DeactivateOfficeCommandHandler],
    _: AdminUserDep,
) -> OfficeResponse:
    logger.info("deactivate_office_started office_id=%s", office_id)
    office = await handler.handle(
        DeactivateOfficeCommand(office_id=office_id),
    )
    logger.info("deactivate_office_finished office_id=%s", office.id)
    return OfficeResponse.from_dto(office)


@router.post("/{office_id}/image", status_code=204)
async def upload_office_image(
    office_id: UUID,
    image: Annotated[UploadFile, File()],
    handler: FromDishka[UploadOfficeImageCommandHandler],
    _: AdminUserDep,
) -> None:
    content_type = image.content_type or ""
    data = await image.read()
    logger.info(
        "upload_office_image_started "
        "office_id=%s content_type=%s size_bytes=%s",
        office_id,
        content_type,
        len(data),
    )
    await handler.handle(
        UploadOfficeImageCommand(
            office_id=office_id,
            content_type=content_type,
            data=data,
        ),
    )
    logger.info("upload_office_image_finished office_id=%s", office_id)


@router.delete("/{office_id}/image", status_code=204)
async def delete_office_image(
    office_id: UUID,
    handler: FromDishka[DeleteOfficeImageCommandHandler],
    _: AdminUserDep,
) -> None:
    logger.info("delete_office_image_started office_id=%s", office_id)
    await handler.handle(DeleteOfficeImageCommand(office_id=office_id))
    logger.info("delete_office_image_finished office_id=%s", office_id)
