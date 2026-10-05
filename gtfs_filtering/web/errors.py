from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from gtfs_filtering.web.services import InvalidGTFSError, UploadTooLargeError


async def _upload_too_large_handler(
    request: Request, exc: UploadTooLargeError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_413_CONTENT_TOO_LARGE,
        content={"detail": str(exc)},
    )


async def _invalid_gtfs_handler(
    request: Request, exc: InvalidGTFSError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": str(exc)},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(UploadTooLargeError, _upload_too_large_handler)
    app.add_exception_handler(InvalidGTFSError, _invalid_gtfs_handler)
