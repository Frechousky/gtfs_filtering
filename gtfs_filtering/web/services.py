import os
import shutil
import tempfile
import threading
import typing
import zipfile

import duckdb
from fastapi import UploadFile

from gtfs_filtering.core import FilterType, perform_filter
from gtfs_filtering.web.config import Settings

INPUT_GTFS_FILENAME = "input_gtfs.zip"
OUTPUT_GTFS_FILENAME = "filtered_gtfs.zip"

# core relies on duckdb default connection which is not thread-safe,
# serialize filterings performed by this process
_FILTER_LOCK = threading.Lock()


class UploadTooLargeError(Exception):
    pass


class UnsafeArchiveError(Exception):
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


def check_archive(
    input_gtfs_zip: str,
    max_uncompressed_size_bytes: int,
    max_entries: int,
    max_compression_ratio: int,
) -> None:
    """
    Checks a zip archive is safe to extract (zip bomb protection)

    Relies on sizes declared in zip headers: zipfile never extracts more bytes than declared
    for an entry (it raises BadZipFile on CRC mismatch instead)

    Args:
        input_gtfs_zip: fullpath of zip archive to check
        max_uncompressed_size_bytes: maximum total uncompressed size of archive entries
        max_entries: maximum number of archive entries
        max_compression_ratio: maximum compression ratio of a single archive entry

    Raises:
        UnsafeArchiveError when a limit is exceeded
    """
    with zipfile.ZipFile(input_gtfs_zip) as archive:
        entries = archive.infolist()
    if len(entries) > max_entries:
        raise UnsafeArchiveError(f"Archive contains more than {max_entries} entries.")
    uncompressed_size = sum(entry.file_size for entry in entries)
    if uncompressed_size > max_uncompressed_size_bytes:
        raise UnsafeArchiveError(
            f"Archive uncompressed size exceeds maximum size of {max_uncompressed_size_bytes} bytes."
        )
    for entry in entries:
        if entry.file_size > max_compression_ratio * max(entry.compress_size, 1):
            raise UnsafeArchiveError(
                f"Archive entry '{entry.filename}' exceeds maximum compression ratio of {max_compression_ratio}."
            )


def filter_gtfs(
    input_gtfs_zip: str,
    directory: str,
    filter_type: FilterType,
    filter_values: typing.List[str],
    settings: Settings,
) -> str:
    """
    Filters a GTFS zip (blocking, must be run in a threadpool)

    Args:
        input_gtfs_zip: fullpath of GTFS zip to filter
        directory: directory to write filtered GTFS zip into
        filter_type: type of filtering to perform
        filter_values: values to keep
        settings: web API settings (archive limits)

    Returns:
        fullpath of filtered GTFS zip

    Raises:
        UnsafeArchiveError when input GTFS exceeds archive limits
        InvalidGTFSError when input GTFS cannot be read or filtered
    """
    if not zipfile.is_zipfile(input_gtfs_zip):
        raise InvalidGTFSError("Uploaded file is not a valid zip archive.")
    check_archive(
        input_gtfs_zip,
        settings.max_uncompressed_size_bytes,
        settings.max_archive_entries,
        settings.max_compression_ratio,
    )
    output_gtfs_zip = os.path.join(directory, OUTPUT_GTFS_FILENAME)
    try:
        with _FILTER_LOCK:
            perform_filter(
                input_gtfs_zip, output_gtfs_zip, filter_type, filter_values, True
            )
    except zipfile.BadZipFile as e:
        raise InvalidGTFSError(f"Uploaded file is not a valid zip archive: {e}") from e
    except (FileNotFoundError, ValueError, duckdb.Error) as e:
        raise InvalidGTFSError(str(e)) from e
    return output_gtfs_zip
