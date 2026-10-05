import typing

from fastapi import APIRouter, File, Form, UploadFile, status
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from gtfs_filtering.core import FilterType
from gtfs_filtering.web import services
from gtfs_filtering.web.dependencies import SettingsDep
from gtfs_filtering.web.schemas import ErrorResponse

router = APIRouter(prefix="/filter", tags=["filtering"])


@router.post(
    "",
    response_class=FileResponse,
    responses={
        status.HTTP_200_OK: {
            "content": {"application/zip": {}},
            "description": "Filtered GTFS zip",
        },
        status.HTTP_413_CONTENT_TOO_LARGE: {"model": ErrorResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorResponse},
    },
)
async def filter_gtfs(
    settings: SettingsDep,
    gtfs_zip: typing.Annotated[UploadFile, File(description="GTFS zip to filter")],
    filter_values: typing.Annotated[
        typing.List[str],
        Form(min_length=1, description="values to keep (route ids or trip ids)"),
    ],
    filter_type: typing.Annotated[
        FilterType, Form(description="type of filtering")
    ] = FilterType.ROUTE_ID,
) -> FileResponse:
    """
    Filters an uploaded GTFS zip by route id or trip id and returns the filtered GTFS zip
    """
    workdir = services.create_workdir()
    try:
        input_gtfs_zip = await services.save_upload(
            gtfs_zip,
            workdir,
            settings.max_upload_size_bytes,
            settings.upload_chunk_size_bytes,
        )
        output_gtfs_zip = await run_in_threadpool(
            services.filter_gtfs,
            input_gtfs_zip,
            workdir,
            filter_type,
            filter_values,
            settings,
        )
    except BaseException:
        # errors are converted to HTTP responses by handlers registered in gtfs_filtering.web.errors
        services.remove_workdir(workdir)
        raise

    return FileResponse(
        output_gtfs_zip,
        media_type="application/zip",
        filename=services.OUTPUT_GTFS_FILENAME,
        # workdir is removed once response has been sent
        background=BackgroundTask(services.remove_workdir, workdir),
    )
