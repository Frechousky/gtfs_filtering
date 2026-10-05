import zipfile

import pytest

from gtfs_filtering.core import FilterType, get_filter_values

AGENCY_TXT = "agency_id,agency_name\nB,Agency B\nA,Agency A\n"
ROUTES_TXT = "route_id,agency_id\nR2,B\nR1,A\nR3,B\n"
TRIPS_TXT = "trip_id,route_id\nT2,R2\nT1,R1\nT3,R3\n"


def make_gtfs_zip(path, entries: dict[str, str]) -> str:
    gtfs_zip = str(path / "gtfs.zip")
    with zipfile.ZipFile(gtfs_zip, "w") as archive:
        for filename, content in entries.items():
            archive.writestr(filename, content)
    return gtfs_zip


def test_get_filter_values__returns_sorted_values(tmp_path):
    gtfs_zip = make_gtfs_zip(
        tmp_path,
        {"agency.txt": AGENCY_TXT, "routes.txt": ROUTES_TXT, "trips.txt": TRIPS_TXT},
    )

    assert get_filter_values(gtfs_zip) == {
        FilterType.AGENCY_ID: ["A", "B"],
        FilterType.ROUTE_ID: ["R1", "R2", "R3"],
        FilterType.TRIP_ID: ["T1", "T2", "T3"],
    }


def test_get_filter_values__when_agency_id_column_is_missing__returns_no_agency_ids(
    tmp_path,
):
    gtfs_zip = make_gtfs_zip(
        tmp_path,
        {
            "agency.txt": "agency_name\nAgency A\n",
            "routes.txt": "route_id\nR1\n",
            "trips.txt": "trip_id,route_id\nT1,R1\n",
        },
    )

    assert get_filter_values(gtfs_zip)[FilterType.AGENCY_ID] == []


def test_get_filter_values__when_required_file_is_missing__raises_file_not_found_error(
    tmp_path,
):
    gtfs_zip = make_gtfs_zip(
        tmp_path, {"agency.txt": AGENCY_TXT, "routes.txt": ROUTES_TXT}
    )

    with pytest.raises(FileNotFoundError, match="file 'trips.txt' is missing"):
        get_filter_values(gtfs_zip)


def test_get_filter_values__when_required_column_is_missing__raises_value_error(
    tmp_path,
):
    gtfs_zip = make_gtfs_zip(
        tmp_path,
        {
            "agency.txt": AGENCY_TXT,
            "routes.txt": "agency_id\nA\n",
            "trips.txt": TRIPS_TXT,
        },
    )

    with pytest.raises(ValueError, match="column 'route_id' is missing"):
        get_filter_values(gtfs_zip)
