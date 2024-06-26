import pandas as pd
import pytest

from gtfs_filtering.core import filter_by_route_id, GTFS


@pytest.fixture
def sample_gtfs():
    agency_data = {"agency_id": ["A"], "agency_name": ["Agency 1"]}
    stops_data = {
        "stop_id": ["S1", "S2", "S3"],
        "stop_name": ["Stop 1", "Stop 2", "Stop 3"],
        "parent_station": [None, None, None],
    }
    routes_data = {
        "route_id": ["R1", "R2", "R3"],
        "route_short_name": ["1", "2", "3"],
        "agency_id": ["A", "A", "A"],
    }
    trips_data = {
        "trip_id": ["T1", "T2", "T3"],
        "route_id": ["R1", "R2", "R3"],
        "service_id": ["S1", "S2", "S2"],
    }
    stop_times_data = {"trip_id": ["T1", "T2", "T3"], "stop_id": ["S1", "S2", "S3"]}
    calendar_data = {"service_id": ["S1", "S2"], "monday": [1, 0], "tuesday": [1, 0]}
    calendar_dates_data = {"service_id": ["S1"], "date": ["20240101"]}

    return GTFS(
        agency=pd.DataFrame(agency_data, dtype=str),
        stops=pd.DataFrame(stops_data, dtype=str),
        routes=pd.DataFrame(routes_data, dtype=str),
        trips=pd.DataFrame(trips_data, dtype=str),
        stop_times=pd.DataFrame(stop_times_data, dtype=str),
        calendar=pd.DataFrame(calendar_data, dtype=str),
        calendar_dates=pd.DataFrame(calendar_dates_data, dtype=str),
    )


def test_filter_by_route_id__filters_correctly(sample_gtfs):
    filtered_gtfs = filter_by_route_id(sample_gtfs, ["R1"])

    assert filtered_gtfs.agency.equals(sample_gtfs.agency), "agency should be equal"
    assert filtered_gtfs.stops.equals(
        pd.DataFrame(
            {"stop_id": ["S1"], "stop_name": ["Stop 1"], "parent_station": [None]}
        )
    ), "stops should be equal"
    assert filtered_gtfs.routes.equals(
        pd.DataFrame(
            {"route_id": ["R1"], "route_short_name": ["1"], "agency_id": ["A"]}
        )
    )
    assert filtered_gtfs.trips.equals(
        pd.DataFrame({"trip_id": ["T1"], "route_id": ["R1"], "service_id": ["S1"]})
    ), "trips should be equal"
    assert filtered_gtfs.stop_times.equals(
        pd.DataFrame({"trip_id": ["T1"], "stop_id": ["S1"]})
    ), "stop_times should be equal"
    assert filtered_gtfs.calendar.equals(
        pd.DataFrame({"service_id": ["S1"], "monday": [1], "tuesday": [1]}, dtype=str)
    ), "calendar should be equal"
    assert filtered_gtfs.calendar_dates.equals(
        sample_gtfs.calendar_dates
    ), "calendar_dates should be equal"


def test_filter_by_route_id__when_no_matching_route_ids__returns_empty_gtfs(
    sample_gtfs,
):
    filtered_gtfs = filter_by_route_id(sample_gtfs, ["R4"])

    assert not filtered_gtfs.agency.empty, "agency should not be empty"
    assert filtered_gtfs.stops.empty, "stops should be empty"
    assert filtered_gtfs.routes.empty, "routes should be empty"
    assert filtered_gtfs.trips.empty, "trips should be empty"
    assert filtered_gtfs.stop_times.empty, "stop_times should be empty"
    assert filtered_gtfs.calendar.empty, "calendar should be empty"
    assert filtered_gtfs.calendar_dates.empty, "calendar_dates should be empty"


def test_filter_by_route_id__multiple_matching_route_ids__filters_correctly(
    sample_gtfs,
):
    # With multiple matching route_ids
    filtered_gtfs = filter_by_route_id(sample_gtfs, ["R1", "R2"])

    assert filtered_gtfs.agency.equals(sample_gtfs.agency), "agency should be equal"
    assert filtered_gtfs.stops.equals(
        pd.DataFrame(
            {
                "stop_id": ["S1", "S2"],
                "stop_name": ["Stop 1", "Stop 2"],
                "parent_station": [None, None],
            }
        )
    ), "stops should be equal"
    assert filtered_gtfs.routes.equals(
        pd.DataFrame(
            {
                "route_id": ["R1", "R2"],
                "route_short_name": ["1", "2"],
                "agency_id": ["A", "A"],
            }
        )
    ), "routes should be equal"
    assert filtered_gtfs.trips.equals(
        pd.DataFrame(
            {
                "trip_id": ["T1", "T2"],
                "route_id": ["R1", "R2"],
                "service_id": ["S1", "S2"],
            }
        )
    ), "trips should be equal"
    assert filtered_gtfs.stop_times.equals(
        pd.DataFrame({"trip_id": ["T1", "T2"], "stop_id": ["S1", "S2"]})
    ), "stop_times should be equal"
    assert filtered_gtfs.calendar.equals(
        pd.DataFrame(
            {"service_id": ["S1", "S2"], "monday": [1, 0], "tuesday": [1, 0]}, dtype=str
        )
    ), "calendar should be equal"
    assert filtered_gtfs.calendar_dates.equals(
        sample_gtfs.calendar_dates
    ), "calendar_dates should be equal"


def test_filter_by_route_id__empty_route_ids__returns_empty_gtfs(sample_gtfs):
    # With empty route_ids
    filtered_gtfs = filter_by_route_id(sample_gtfs, [])

    assert not filtered_gtfs.agency.empty, "agency should not be empty"
    assert filtered_gtfs.stops.empty, "stops should be empty"
    assert filtered_gtfs.routes.empty, "routes should be empty"
    assert filtered_gtfs.trips.empty, "trips should be empty"
    assert filtered_gtfs.stop_times.empty, "stop_times should be empty"
    assert filtered_gtfs.calendar.empty, "calendar should be empty"
    assert filtered_gtfs.calendar_dates.empty, "calendar_dates should be empty"


def test_filter_by_route_id__no_calendar__handles_correctly(sample_gtfs):
    sample_gtfs_no_calendar = GTFS(**sample_gtfs.__dict__)
    sample_gtfs_no_calendar.calendar = None

    filtered_gtfs_no_calendar = filter_by_route_id(sample_gtfs_no_calendar, ["R1"])
    assert filtered_gtfs_no_calendar.agency.equals(
        sample_gtfs_no_calendar.agency
    ), "agency should be equal"
    assert filtered_gtfs_no_calendar.stops.equals(
        pd.DataFrame(
            {"stop_id": ["S1"], "stop_name": ["Stop 1"], "parent_station": [None]}
        )
    ), "stops should be equal"
    assert filtered_gtfs_no_calendar.trips.equals(
        pd.DataFrame({"trip_id": ["T1"], "route_id": ["R1"], "service_id": ["S1"]})
    ), "trips should be equal"
    assert filtered_gtfs_no_calendar.stop_times.equals(
        pd.DataFrame({"trip_id": ["T1"], "stop_id": ["S1"]})
    ), "stop_times should be equal"
    assert filtered_gtfs_no_calendar.calendar is None, "calendar should be none"
    assert filtered_gtfs_no_calendar.calendar_dates.equals(
        sample_gtfs_no_calendar.calendar_dates
    ), "calendar_dates should be equal"


def test_filter_by_route_id__no_calendar_dates__handles_correctly(sample_gtfs):
    sample_gtfs_no_calendar_dates = GTFS(**sample_gtfs.__dict__)
    sample_gtfs_no_calendar_dates.calendar_dates = None

    filtered_gtfs_no_calendar_dates = filter_by_route_id(
        sample_gtfs_no_calendar_dates, ["R1"]
    )
    assert filtered_gtfs_no_calendar_dates.agency.equals(
        filtered_gtfs_no_calendar_dates.agency
    ), "agency should be equal"
    assert filtered_gtfs_no_calendar_dates.stops.equals(
        pd.DataFrame(
            {"stop_id": ["S1"], "stop_name": ["Stop 1"], "parent_station": [None]}
        )
    ), "stops should be equal"
    assert filtered_gtfs_no_calendar_dates.trips.equals(
        pd.DataFrame({"trip_id": ["T1"], "route_id": ["R1"], "service_id": ["S1"]})
    ), "trips should be equal"
    assert filtered_gtfs_no_calendar_dates.stop_times.equals(
        pd.DataFrame({"trip_id": ["T1"], "stop_id": ["S1"]})
    ), "stop_times should be equal"
    assert filtered_gtfs_no_calendar_dates.calendar.equals(
        filtered_gtfs_no_calendar_dates.calendar
    ), "calendar_dates should be equal"
    assert (
        filtered_gtfs_no_calendar_dates.calendar_dates is None
    ), "calendar_dates should be none"
