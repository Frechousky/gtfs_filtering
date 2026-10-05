import functools
import pathlib

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from gtfs_filtering.web.dependencies import SettingsDep

INDEX_HTML = pathlib.Path(__file__).parent.parent / "static" / "index.html"

router = APIRouter(tags=["ui"])


@functools.lru_cache
def _read_index_html() -> str:
    return INDEX_HTML.read_text(encoding="utf-8")


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index(settings: SettingsDep) -> HTMLResponse:
    """HTML page to filter a GTFS zip through the web API"""
    html = _read_index_html().replace(
        "{{MAX_UPLOAD_SIZE_MB}}", str(settings.max_upload_size_mb)
    )
    return HTMLResponse(html)
