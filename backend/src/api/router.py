from fastapi import APIRouter

from api.routes.auth import router as auth_router
from api.routes.bookings import router as bookings_router
from api.routes.offices import router as offices_router
from api.routes.rooms import router as rooms_router
from api.routes.users import router as users_router

API_PREFIX = "/api"
API_VERSION = "v1"
API_V1_PREFIX = f"{API_PREFIX}/{API_VERSION}"

v1_router = APIRouter(prefix=f"/{API_VERSION}")
v1_router.include_router(offices_router, prefix="/offices")
v1_router.include_router(rooms_router, prefix="/rooms")
v1_router.include_router(bookings_router, prefix="/bookings")
v1_router.include_router(users_router, prefix="/users")
v1_router.include_router(auth_router, prefix="/auth")

api_router = APIRouter(prefix=API_PREFIX)
api_router.include_router(v1_router)
