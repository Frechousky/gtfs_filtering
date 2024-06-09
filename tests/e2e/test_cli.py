import io
import os
import subprocess
import typing
import zipfile

import pandas as pd
import pytest

from gtfs_filtering.core import get_unique_not_null_column_values
from tests.e2e.conftest import ROOT_FOLDER

CLI_PATH = os.path.join(ROOT_FOLDER, "dist", "cli")


def test_cli__when_filtering_by_route_id__filters_by_route_id(
    gtfs_nyc: str, output_gtfs: str, route_ids: typing.List[str], validate_gtfs
):
    output = subprocess.run(
        [CLI_PATH, gtfs_nyc, output_gtfs, *route_ids], capture_output=True, text=True
    )

    assert output.returncode == 0, "command is successful"
    assert os.path.isfile(output_gtfs), "output_gtfs is created"

    # validate output GTFS
    validation_output = validate_gtfs(output_gtfs)
    assert validation_output.returncode == 0, "output GTFS is valid"

    output_gtfs_zip = zipfile.ZipFile(output_gtfs)
    routes_bytes = output_gtfs_zip.read("routes.txt")
    routes_str = io.StringIO(routes_bytes.decode("UTF-8"))
    routes = pd.read_csv(routes_str)
    output_route_ids = get_unique_not_null_column_values(routes, "route_id").sort()
    expected_route_ids = route_ids.sort()
    assert (
        output_route_ids == expected_route_ids
    ), "output GTFS is filtered by route_ids"


def test_cli__when_filtering_by_trip_id__filters_by_trip_id(
    gtfs_nyc: str, output_gtfs: str, trip_ids: typing.List[str], validate_gtfs
):
    output = subprocess.run(
        [CLI_PATH, "--filter-type", "trip_id", gtfs_nyc, output_gtfs, *trip_ids],
        capture_output=True,
        text=True,
    )

    assert output.returncode == 0, "command is successful"
    assert os.path.isfile(output_gtfs), "output_gtfs is created"

    # validate output GTFS
    validation_output = validate_gtfs(output_gtfs)
    assert validation_output.returncode == 0, "output GTFS is valid"

    output_gtfs_zip = zipfile.ZipFile(output_gtfs)
    trips_bytes = output_gtfs_zip.read("trips.txt")
    trips_str = io.StringIO(trips_bytes.decode("UTF-8"))
    trips = pd.read_csv(trips_str)
    output_trip_ids = get_unique_not_null_column_values(trips, "trip_id").sort()
    expected_trip_ids = trip_ids.sort()
    assert output_trip_ids == expected_trip_ids, "output GTFS is filtered by trip_ids"


@pytest.mark.parametrize(
    "args",
    [
        ["--help"],
        ["--help", "gtfs.zip", "output.zip"],
        ["gtfs.zip", "--help", "output.zip"],
        ["gtfs.zip", "output.zip", "--help"],
        ["--help", "gtfs.zip", "output.zip", "--help"],
    ],
)
def test_cli__when_help_option_is_present__displays_help(args: typing.List[str]):
    output = subprocess.run([CLI_PATH, *args], capture_output=True, text=True)

    assert output.returncode == 0, "command should be successful"
    assert "Usage: cli" in output.stdout, "command should display help message to user"


def test_cli__when_input_gtfs_zip_arg_is_missing__fails_and_displays_error_message():
    output = subprocess.run(CLI_PATH, capture_output=True, text=True)

    assert output.returncode != 0, "command should fail"
    assert "Usage: cli" in output.stderr, "command should display help message to user"
    assert (
        "Error: Missing argument 'INPUT_GTFS_ZIP'." in output.stderr
    ), "command should display error message to user"


def test_cli__when_input_gtfs_zip_does_not_exists__fails_and_displays_error_message():
    output = subprocess.run(
        [CLI_PATH, "non_existing_file.zip"], capture_output=True, text=True
    )

    assert output.returncode != 0, "command should fail"
    assert "Usage: cli" in output.stderr, "command should display help message to user"
    assert (
        "Invalid value for 'INPUT_GTFS_ZIP': File 'non_existing_file.zip' does not exist."
        in output.stderr
    ), "command should display error message to user"


def test_cli__when_output_gtfs_zip_arg_is_missing__fails_and_displays_error_message(
    gtfs_nyc: str
):
    output = subprocess.run([CLI_PATH, gtfs_nyc], capture_output=True, text=True)

    assert output.returncode != 0, "command should fail"
    assert "Usage: cli" in output.stderr, "command should display help message to user"
    assert (
        "Error: Missing argument 'OUTPUT_GTFS_ZIP'." in output.stderr
    ), "command should display error message to user"


def test_cli__when_output_gtfs_zip_exists_and_overwrite_flag_not_set__fails_and_displays_error_message(
    gtfs_nyc: str, existing_output_gtfs: str, route_ids: typing.List[str]
):
    assert os.path.isfile(existing_output_gtfs), "output_gtfs exists"

    output = subprocess.run(
        [CLI_PATH, gtfs_nyc, existing_output_gtfs, *route_ids],
        capture_output=True,
        text=True,
    )

    assert output.returncode != 0, "command should fail"
    assert (
        f"Error: File '{existing_output_gtfs}' already exists." in output.stderr
    ), "command should display error message to user"


@pytest.mark.parametrize("overwrite_opt", ["-o", "--overwrite"])
def test_cli__when_output_gtfs_zip_exists_and_overwrite_flag_set__is_successful(
    gtfs_nyc: str,
    existing_output_gtfs: str,
    route_ids: typing.List[str],
    overwrite_opt: str,
):
    assert os.path.isfile(existing_output_gtfs), "output_gtfs exists"
    mtime_before = os.path.getmtime(existing_output_gtfs)

    output = subprocess.run(
        [CLI_PATH, overwrite_opt, gtfs_nyc, existing_output_gtfs, *route_ids],
        capture_output=True,
        text=True,
    )

    assert output.returncode == 0, "command is successful"
    assert (
        os.path.getmtime(existing_output_gtfs) > mtime_before
    ), "output gtfs should be overwritten"


def test_cli__when_required_file_is_missing_in_input_gtfs_zip__fails_and_displays_error_message(
    gtfs_missing_routes_txt: str, output_gtfs: str, route_ids: typing.List[str]
):
    output = subprocess.run(
        [CLI_PATH, gtfs_missing_routes_txt, output_gtfs, *route_ids],
        capture_output=True,
        text=True,
    )

    assert output.returncode != 0, "command should fail"
    assert (
        "Error: GTFS is invalid: file 'routes.txt' is missing." in output.stderr
    ), "command should display error message to user"


def test_cli__when_required_file_is_empty_in_input_gtfs_zip__fails_and_displays_error_message(
    gtfs_empty_routes_txt: str, output_gtfs: str, route_ids: typing.List[str]
):
    output = subprocess.run(
        [CLI_PATH, gtfs_empty_routes_txt, output_gtfs, *route_ids],
        capture_output=True,
        text=True,
    )

    assert output.returncode != 0, "command should fail"
    assert (
        "Error: No columns to parse from file 'routes.txt'." in output.stderr
    ), "command should display error message to user"
