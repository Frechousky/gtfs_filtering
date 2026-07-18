import pytest

from gtfs_filtering.core import filter_by_route_id, GTFS
from tests.unit.conftest import make_relation, relations_equal, is_empty


@pytest.fixture
def sample_gtfs():
    agency = make_relation({"agency_id": ["A"], "agency_name": ["Agency 1"]})
    stops = make_relation(
        {
            "stop_id": ["S1", "S2", "S3"],
            "stop_name": ["Stop 1", "Stop 2", "Stop 3"],
            "parent_station": [None, None, None],
        }
    )
    routes = make_relation(
        {
            "route_id": ["R1", "R2", "R3"],
            "route_short_name": ["1", "2", "3"],
            "agency_id": ["A", "A", "A"],
        }
    )
    trips = make_relation(
        {
            "trip_id": ["T1", "T2", "T3"],
            "route_id": ["R1", "R2", "R3"],
            "service_id": ["S1", "S2", "S2"],
        }
    )
    stop_times = make_relation(
        {"trip_id": ["T1", "T2", "T3"], "stop_id": ["S1", "S2", "S3"]}
    )
    calendar = make_relation(
        {"service_id": ["S1", "S2"], "monday": ["1", "0"], "tuesday": ["1", "0"]}
    )
    calendar_dates = make_relation({"service_id": ["S1"], "date": ["20240101"]})

    return GTFS(
        agency=agency,
        stops=stops,
        routes=routes,
        trips=trips,
        stop_times=stop_times,
        calendar=calendar,
        calendar_dates=calendar_dates,
    )


def test_filter_by_route_id__filters_correctly(sample_gtfs):
    filtered_gtfs = filter_by_route_id(sample_gtfs, ["R1"])

    assert relations_equal(filtered_gtfs.agency, sample_gtfs.agency), (
        "agency should be equal"
    )
    assert relations_equal(
        filtered_gtfs.stops,
        make_relation(
            {"stop_id": ["S1"], "stop_name": ["Stop 1"], "parent_station": [None]}
        ),
    ), "stops should be equal"
    assert relations_equal(
        filtered_gtfs.routes,
        make_relation(
            {"route_id": ["R1"], "route_short_name": ["1"], "agency_id": ["A"]}
        ),
    )
    assert relations_equal(
        filtered_gtfs.trips,
        make_relation({"trip_id": ["T1"], "route_id": ["R1"], "service_id": ["S1"]}),
    ), "trips should be equal"
    assert relations_equal(
        filtered_gtfs.stop_times,
        make_relation({"trip_id": ["T1"], "stop_id": ["S1"]}),
    ), "stop_times should be equal"
    assert relations_equal(
        filtered_gtfs.calendar,
        make_relation({"service_id": ["S1"], "monday": ["1"], "tuesday": ["1"]}),
    ), "calendar should be equal"
    assert relations_equal(filtered_gtfs.calendar_dates, sample_gtfs.calendar_dates), (
        "calendar_dates should be equal"
    )


def test_filter_by_route_id__when_no_matching_route_ids__returns_empty_gtfs(
    sample_gtfs,
):
    filtered_gtfs = filter_by_route_id(sample_gtfs, ["R4"])

    assert not is_empty(filtered_gtfs.agency), "agency should not be empty"
    assert is_empty(filtered_gtfs.stops), "stops should be empty"
    assert is_empty(filtered_gtfs.routes), "routes should be empty"
    assert is_empty(filtered_gtfs.trips), "trips should be empty"
    assert is_empty(filtered_gtfs.stop_times), "stop_times should be empty"
    assert is_empty(filtered_gtfs.calendar), "calendar should be empty"
    assert is_empty(filtered_gtfs.calendar_dates), "calendar_dates should be empty"


def test_filter_by_route_id__multiple_matching_route_ids__filters_correctly(
    sample_gtfs,
):
    filtered_gtfs = filter_by_route_id(sample_gtfs, ["R1", "R2"])

    assert relations_equal(filtered_gtfs.agency, sample_gtfs.agency), (
        "agency should be equal"
    )
    assert relations_equal(
        filtered_gtfs.stops,
        make_relation(
            {
                "stop_id": ["S1", "S2"],
                "stop_name": ["Stop 1", "Stop 2"],
                "parent_station": [None, None],
            }
        ),
    ), "stops should be equal"
    assert relations_equal(
        filtered_gtfs.routes,
        make_relation(
            {
                "route_id": ["R1", "R2"],
                "route_short_name": ["1", "2"],
                "agency_id": ["A", "A"],
            }
        ),
    ), "routes should be equal"
    assert relations_equal(
        filtered_gtfs.trips,
        make_relation(
            {
                "trip_id": ["T1", "T2"],
                "route_id": ["R1", "R2"],
                "service_id": ["S1", "S2"],
            }
        ),
    ), "trips should be equal"
    assert relations_equal(
        filtered_gtfs.stop_times,
        make_relation({"trip_id": ["T1", "T2"], "stop_id": ["S1", "S2"]}),
    ), "stop_times should be equal"
    assert relations_equal(
        filtered_gtfs.calendar,
        make_relation(
            {"service_id": ["S1", "S2"], "monday": ["1", "0"], "tuesday": ["1", "0"]}
        ),
    ), "calendar should be equal"
    assert relations_equal(filtered_gtfs.calendar_dates, sample_gtfs.calendar_dates), (
        "calendar_dates should be equal"
    )


def test_filter_by_route_id__empty_route_ids__returns_empty_gtfs(sample_gtfs):
    filtered_gtfs = filter_by_route_id(sample_gtfs, [])

    assert not is_empty(filtered_gtfs.agency), "agency should not be empty"
    assert is_empty(filtered_gtfs.stops), "stops should be empty"
    assert is_empty(filtered_gtfs.routes), "routes should be empty"
    assert is_empty(filtered_gtfs.trips), "trips should be empty"
    assert is_empty(filtered_gtfs.stop_times), "stop_times should be empty"
    assert is_empty(filtered_gtfs.calendar), "calendar should be empty"
    assert is_empty(filtered_gtfs.calendar_dates), "calendar_dates should be empty"


def test_filter_by_route_id__no_calendar__handles_correctly(sample_gtfs):
    sample_gtfs_no_calendar = GTFS(**sample_gtfs.__dict__)
    sample_gtfs_no_calendar.calendar = None

    filtered_gtfs_no_calendar = filter_by_route_id(sample_gtfs_no_calendar, ["R1"])
    assert relations_equal(
        filtered_gtfs_no_calendar.agency, sample_gtfs_no_calendar.agency
    ), "agency should be equal"
    assert relations_equal(
        filtered_gtfs_no_calendar.stops,
        make_relation(
            {"stop_id": ["S1"], "stop_name": ["Stop 1"], "parent_station": [None]}
        ),
    ), "stops should be equal"
    assert relations_equal(
        filtered_gtfs_no_calendar.trips,
        make_relation({"trip_id": ["T1"], "route_id": ["R1"], "service_id": ["S1"]}),
    ), "trips should be equal"
    assert relations_equal(
        filtered_gtfs_no_calendar.stop_times,
        make_relation({"trip_id": ["T1"], "stop_id": ["S1"]}),
    ), "stop_times should be equal"
    assert filtered_gtfs_no_calendar.calendar is None, "calendar should be none"
    assert relations_equal(
        filtered_gtfs_no_calendar.calendar_dates, sample_gtfs_no_calendar.calendar_dates
    ), "calendar_dates should be equal"


def test_filter_by_route_id__no_calendar_dates__handles_correctly(sample_gtfs):
    sample_gtfs_no_calendar_dates = GTFS(**sample_gtfs.__dict__)
    sample_gtfs_no_calendar_dates.calendar_dates = None

    filtered_gtfs_no_calendar_dates = filter_by_route_id(
        sample_gtfs_no_calendar_dates, ["R1"]
    )
    assert relations_equal(
        filtered_gtfs_no_calendar_dates.agency, filtered_gtfs_no_calendar_dates.agency
    ), "agency should be equal"
    assert relations_equal(
        filtered_gtfs_no_calendar_dates.stops,
        make_relation(
            {"stop_id": ["S1"], "stop_name": ["Stop 1"], "parent_station": [None]}
        ),
    ), "stops should be equal"
    assert relations_equal(
        filtered_gtfs_no_calendar_dates.trips,
        make_relation({"trip_id": ["T1"], "route_id": ["R1"], "service_id": ["S1"]}),
    ), "trips should be equal"
    assert relations_equal(
        filtered_gtfs_no_calendar_dates.stop_times,
        make_relation({"trip_id": ["T1"], "stop_id": ["S1"]}),
    ), "stop_times should be equal"
    assert relations_equal(
        filtered_gtfs_no_calendar_dates.calendar,
        filtered_gtfs_no_calendar_dates.calendar,
    ), "calendar_dates should be equal"
    assert filtered_gtfs_no_calendar_dates.calendar_dates is None, (
        "calendar_dates should be none"
    )
