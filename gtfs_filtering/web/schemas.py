from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str = "ok"


class ErrorResponse(BaseModel):
    detail: str


class FilterValuesResponse(BaseModel):
    """Values available for each filter type, sorted"""

    route_ids: list[str]
    trip_ids: list[str]
    agency_ids: list[str]
