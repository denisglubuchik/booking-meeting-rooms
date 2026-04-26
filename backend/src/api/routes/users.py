from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

router = APIRouter(tags=["Users"], route_class=DishkaRoute)
