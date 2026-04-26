from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from api.routes.bookings import router as bookings_router
from api.routes.offices import router as offices_router
from api.routes.rooms import router as rooms_router
from api.routes.users import router as users_router
from infra.dependencies import container

app = FastAPI(title="Booking meeting rooms API")


@app.get("/healthcheck", status_code=200, tags=["General"])
def check_service_health() -> None:
    return


app.include_router(offices_router, prefix="/offices")
app.include_router(rooms_router, prefix="/rooms")
app.include_router(bookings_router, prefix="/bookings")
app.include_router(users_router, prefix="/users")


setup_dishka(container, app)
