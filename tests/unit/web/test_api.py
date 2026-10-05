import io
import os
import typing
import zipfile

import duckdb
import pytest
from fastapi.testclient import TestClient

from gtfs_filtering.core import get_unique_not_null_column_values
from gtfs_filtering.web.config import Settings, get_settings
from gtfs_filtering.web.main import create_app

DATA_FOLDER = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data")
)
FILTER_URL = "/api/v1/filter"


@pytest.fixture()
def client() -> typing.Iterator[TestClient]:
    with TestClient(create_app()) as c:
        yield c


def read_gtfs(filename: str) -> bytes:
    with open(os.path.join(DATA_FOLDER, filename), "rb") as f:
        return f.read()


def read_output_column(
    content: bytes, gtfs_file: str, col_name: str
) -> typing.List[str]:
    output_gtfs_zip = zipfile.ZipFile(io.BytesIO(content))
    file_str = io.StringIO(output_gtfs_zip.read(gtfs_file).decode("UTF-8"))
    rel = duckdb.read_csv(file_str, all_varchar=True)
    return sorted(get_unique_not_null_column_values(rel, col_name))


def test_health__returns_ok(client: TestClient):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_filter__when_filtering_by_route_id__returns_filtered_gtfs(
    client: TestClient,
):
    response = client.post(
        FILTER_URL,
        files={"gtfs_zip": ("gtfs.zip", read_gtfs("gtfs_nyc.zip"), "application/zip")},
        data={"filter_values": ["1", "2"]},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"
    assert read_output_column(response.content, "routes.txt", "route_id") == [
        "1",
        "2",
    ]


def test_filter__when_filtering_by_trip_id__returns_filtered_gtfs(
    client: TestClient,
):
    trip_id = "AFA23GEN-1038-Sunday-00_000600_1..S03R"
    response = client.post(
        FILTER_URL,
        files={"gtfs_zip": ("gtfs.zip", read_gtfs("gtfs_nyc.zip"), "application/zip")},
        data={"filter_type": "trip_id", "filter_values": [trip_id]},
    )

    assert response.status_code == 200
    assert read_output_column(response.content, "trips.txt", "trip_id") == [trip_id]


def test_filter__when_filter_values_are_missing__returns_422(client: TestClient):
    response = client.post(
        FILTER_URL,
        files={"gtfs_zip": ("gtfs.zip", read_gtfs("gtfs_nyc.zip"), "application/zip")},
    )

    assert response.status_code == 422


def test_filter__when_filter_type_is_invalid__returns_422(client: TestClient):
    response = client.post(
        FILTER_URL,
        files={"gtfs_zip": ("gtfs.zip", read_gtfs("gtfs_nyc.zip"), "application/zip")},
        data={"filter_type": "stop_id", "filter_values": ["1"]},
    )

    assert response.status_code == 422


def test_filter__when_uploaded_file_is_not_a_zip__returns_422(client: TestClient):
    response = client.post(
        FILTER_URL,
        files={"gtfs_zip": ("gtfs.zip", b"not a zip", "application/zip")},
        data={"filter_values": ["1"]},
    )

    assert response.status_code == 422
    assert response.json() == {"detail": "Uploaded file is not a valid zip archive."}


def test_filter__when_required_file_is_missing__returns_422(client: TestClient):
    response = client.post(
        FILTER_URL,
        files={
            "gtfs_zip": (
                "gtfs.zip",
                read_gtfs("gtfs_missing_routes_txt.zip"),
                "application/zip",
            )
        },
        data={"filter_values": ["1"]},
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "GTFS is invalid: file 'routes.txt' is missing."
    }


def test_filter__when_required_file_is_empty__returns_422(client: TestClient):
    response = client.post(
        FILTER_URL,
        files={
            "gtfs_zip": (
                "gtfs.zip",
                read_gtfs("gtfs_empty_routes_txt.zip"),
                "application/zip",
            )
        },
        data={"filter_values": ["1"]},
    )

    assert response.status_code == 422
    assert response.json() == {"detail": "No columns to parse from file 'routes.txt'."}


def test_filter__when_uploaded_file_is_too_large__returns_413():
    app = create_app()
    app.dependency_overrides[get_settings] = lambda: Settings(
        max_upload_size_mb=0, upload_chunk_size_bytes=1
    )
    with TestClient(app) as client:
        response = client.post(
            FILTER_URL,
            files={"gtfs_zip": ("gtfs.zip", b"PK", "application/zip")},
            data={"filter_values": ["1"]},
        )

    assert response.status_code == 413
