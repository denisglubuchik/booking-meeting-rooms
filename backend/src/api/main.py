import logging

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.errors import register_exception_handlers
from api.middleware import register_middlewares
from api.routes.bookings import router as bookings_router
from api.routes.offices import router as offices_router
from api.routes.rooms import router as rooms_router
from api.routes.users import router as users_router
from core.config import LoggingConfig
from core.logging import setup_logging
from infra.dependencies import container

setup_logging(LoggingConfig())
logger = logging.getLogger("api.main")

app = FastAPI(title="Booking meeting rooms API")
register_exception_handlers(app)
register_middlewares(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthcheck", status_code=200, tags=["General"])
def check_service_health() -> None:
    return


app.include_router(offices_router, prefix="/offices")
app.include_router(rooms_router, prefix="/rooms")
app.include_router(bookings_router, prefix="/bookings")
app.include_router(users_router, prefix="/users")


setup_dishka(container, app)
logger.info("application_initialized title=%s", app.title)
