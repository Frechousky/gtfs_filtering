import os

import duckdb
import pytest

from gtfs_filtering.core import GTFS, save_gtfs
from tests.unit.conftest import make_relation, relations_equal


@pytest.fixture
def gtfs_data():
    stops = make_relation({"stop_id": ["1", "2"], "stop_name": ["Stop 1", "Stop 2"]})
    routes = make_relation(
        {"route_id": ["100", "200"], "route_name": ["Route 100", "Route 200"]}
    )
    trips = make_relation({"trip_id": ["1000", "2000"], "route_id": ["100", "200"]})
    stop_times = make_relation({"trip_id": ["1000", "2000"], "stop_id": ["1", "2"]})
    return GTFS(stops=stops, routes=routes, trips=trips, stop_times=stop_times)


def test_save_gtfs__when_all_files_are_present__all_files_are_saved(
    gtfs_data, tmp_path
):
    save_gtfs(gtfs_data, tmp_path)

    assert os.path.isfile(os.path.join(tmp_path, "stops.txt")), "file should be saved"
    assert os.path.isfile(os.path.join(tmp_path, "routes.txt")), "file should be saved"
    assert os.path.isfile(os.path.join(tmp_path, "trips.txt")), "file should be saved"
    assert os.path.isfile(os.path.join(tmp_path, "stop_times.txt")), (
        "file should be saved"
    )


def test_save_gtfs__when_all_files_are_present__content_is_correct(gtfs_data, tmp_path):
    save_gtfs(gtfs_data, tmp_path)

    stops_rel = duckdb.read_csv(os.path.join(tmp_path, "stops.txt"), all_varchar=True)
    routes_rel = duckdb.read_csv(os.path.join(tmp_path, "routes.txt"), all_varchar=True)
    trips_rel = duckdb.read_csv(os.path.join(tmp_path, "trips.txt"), all_varchar=True)
    stop_times_rel = duckdb.read_csv(
        os.path.join(tmp_path, "stop_times.txt"), all_varchar=True
    )

    assert relations_equal(stops_rel, gtfs_data.stops), "frames should be equal"
    assert relations_equal(routes_rel, gtfs_data.routes), "frames should be equal"
    assert relations_equal(trips_rel, gtfs_data.trips), "frames should be equal"
    assert relations_equal(stop_times_rel, gtfs_data.stop_times), (
        "frames should be equal"
    )


def test_save_gtfs__when_some_files_none__only_non_none_files_saved(tmp_path):
    gtfs_data = GTFS(
        stops=make_relation({"stop_id": ["1"], "stop_name": ["Stop 1"]}),
        routes=None,
        trips=make_relation({"trip_id": ["1000"], "route_id": ["100"]}),
        stop_times=None,
    )

    save_gtfs(gtfs_data, tmp_path)

    assert os.path.isfile(os.path.join(tmp_path, "stops.txt")), "file should be saved"
    assert os.path.isfile(os.path.join(tmp_path, "trips.txt")), "file should be saved"

    assert not os.path.isfile(os.path.join(tmp_path, "routes.txt")), (
        "file should not be saved"
    )
    assert not os.path.isfile(os.path.join(tmp_path, "stop_times.txt")), (
        "file should not be saved"
    )


def test_save_gtfs__when_all_files_none__no_files_saved(tmp_path):
    gtfs_data = GTFS()

    save_gtfs(gtfs_data, tmp_path)

    assert not os.path.isfile(os.path.join(tmp_path, "stops.txt")), (
        "file should not be saved"
    )
    assert not os.path.isfile(os.path.join(tmp_path, "routes.txt")), (
        "file should not be saved"
    )
    assert not os.path.isfile(os.path.join(tmp_path, "trips.txt")), (
        "file should not be saved"
    )
    assert not os.path.isfile(os.path.join(tmp_path, "stop_times.txt")), (
        "file should not be saved"
    )


def test_save_gtfs__when_directory_does_not_exist__raises_os_error(gtfs_data):
    non_existent_dir = "non_existent_directory"
    assert not os.path.isdir(non_existent_dir), "directory shound not exist"

    with pytest.raises(OSError):
        save_gtfs(gtfs_data, non_existent_dir)


def test_save_gtfs__when_directory_is_not_writable__raises_permission_error(
    gtfs_data, tmp_path
):
    # Create a non-writable directory
    unwritable_directory = os.path.join(tmp_path, "unwritable_directory")
    os.makedirs(unwritable_directory)
    os.chmod(unwritable_directory, 0o400)  # Read-only

    with pytest.raises(PermissionError):
        save_gtfs(gtfs_data, unwritable_directory)

    # Restore permissions for cleanup
    os.chmod(unwritable_directory, 0o700)
