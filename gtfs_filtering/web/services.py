import os
import shutil
import tempfile
import threading
import typing
import zipfile

import duckdb
from fastapi import UploadFile

from gtfs_filtering.core import FilterType, perform_filter

INPUT_GTFS_FILENAME = "input_gtfs.zip"
OUTPUT_GTFS_FILENAME = "filtered_gtfs.zip"

# core relies on duckdb default connection which is not thread-safe,
# serialize filterings performed by this process
_FILTER_LOCK = threading.Lock()


class UploadTooLargeError(Exception):
    pass


class InvalidGTFSError(ValueError):
    pass


def create_workdir() -> str:
    """Creates a temporary directory dedicated to a single request"""
    return tempfile.mkdtemp(prefix="gtfs-filtering-web-")


def remove_workdir(workdir: str) -> None:
    shutil.rmtree(workdir, ignore_errors=True)


async def save_upload(
    upload: UploadFile, directory: str, max_size_bytes: int, chunk_size_bytes: int
) -> str:
    """
    Streams an uploaded file to disk

    Args:
        upload: uploaded file
        directory: directory to save uploaded file into
        max_size_bytes: maximum accepted size of uploaded file
        chunk_size_bytes: size of chunks read from uploaded file

    Returns:
        fullpath of saved file

    Raises:
        UploadTooLargeError when uploaded file is bigger than max_size_bytes
    """
    path = os.path.join(directory, INPUT_GTFS_FILENAME)
    size = 0
    with open(path, "wb") as f:
        while chunk := await upload.read(chunk_size_bytes):
            size += len(chunk)
            if size > max_size_bytes:
                raise UploadTooLargeError(
                    f"Uploaded file exceeds maximum size of {max_size_bytes} bytes."
                )
            f.write(chunk)
    return path


def filter_gtfs(
    input_gtfs_zip: str,
    directory: str,
    filter_type: FilterType,
    filter_values: typing.List[str],
) -> str:
    """
    Filters a GTFS zip (blocking, must be run in a threadpool)

    Args:
        input_gtfs_zip: fullpath of GTFS zip to filter
        directory: directory to write filtered GTFS zip into
        filter_type: type of filtering to perform
        filter_values: values to keep

    Returns:
        fullpath of filtered GTFS zip

    Raises:
        InvalidGTFSError when input GTFS cannot be read or filtered
    """
    if not zipfile.is_zipfile(input_gtfs_zip):
        raise InvalidGTFSError("Uploaded file is not a valid zip archive.")
    output_gtfs_zip = os.path.join(directory, OUTPUT_GTFS_FILENAME)
    try:
        with _FILTER_LOCK:
            perform_filter(
                input_gtfs_zip, output_gtfs_zip, filter_type, filter_values, True
            )
    except (FileNotFoundError, ValueError, duckdb.Error) as e:
        raise InvalidGTFSError(str(e)) from e
    return output_gtfs_zip
