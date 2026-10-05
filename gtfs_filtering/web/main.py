from fastapi import FastAPI

from gtfs_filtering.web.config import get_settings
from gtfs_filtering.web.errors import register_exception_handlers
from gtfs_filtering.web.routers import filtering, health

API_V1_PREFIX = "/api/v1"


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        summary="Filter a GTFS feed by route ID or trip ID",
    )
    register_exception_handlers(app)
    app.include_router(health.router)
    app.include_router(filtering.router, prefix=API_V1_PREFIX)
    return app


app = create_app()
