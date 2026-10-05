import pytest

from gtfs_filtering.core import GTFS, filter_by_agency_id
from tests.unit.conftest import is_empty, make_relation, relations_equal


@pytest.fixture
def sample_gtfs():
    agency = make_relation(
        {"agency_id": ["A", "B"], "agency_name": ["Agency A", "Agency B"]}
    )
    stops = make_relation({"stop_id": ["S1", "S2"], "stop_name": ["Stop 1", "Stop 2"]})
    routes = make_relation(
        {"route_id": ["R1", "R2", "R3"], "agency_id": ["A", "B", "B"]}
    )
    trips = make_relation(
        {
            "trip_id": ["T1", "T2", "T3"],
            "route_id": ["R1", "R2", "R3"],
            "service_id": ["SV1", "SV2", "SV2"],
        }
    )
    stop_times = make_relation(
        {"trip_id": ["T1", "T2", "T3"], "stop_id": ["S1", "S2", "S2"]}
    )
    return GTFS(
        agency=agency, stops=stops, routes=routes, trips=trips, stop_times=stop_times
    )


@pytest.fixture
def single_agency_gtfs():
    agency = make_relation({"agency_id": ["A"], "agency_name": ["Agency A"]})
    stops = make_relation({"stop_id": ["S1"], "stop_name": ["Stop 1"]})
    # agency_id is not mandatory in routes.txt when there is a single agency
    routes = make_relation({"route_id": ["R1", "R2"]})
    trips = make_relation(
        {"trip_id": ["T1", "T2"], "route_id": ["R1", "R2"], "service_id": ["SV1"] * 2}
    )
    stop_times = make_relation({"trip_id": ["T1", "T2"], "stop_id": ["S1", "S1"]})
    return GTFS(
        agency=agency, stops=stops, routes=routes, trips=trips, stop_times=stop_times
    )


def test_filter_by_agency_id__filters_correctly(sample_gtfs):
    filtered_gtfs = filter_by_agency_id(sample_gtfs, ["B"])

    assert relations_equal(
        filtered_gtfs.agency,
        make_relation({"agency_id": ["B"], "agency_name": ["Agency B"]}),
    )
    assert relations_equal(
        filtered_gtfs.routes,
        make_relation({"route_id": ["R2", "R3"], "agency_id": ["B", "B"]}),
    )
    assert relations_equal(
        filtered_gtfs.trips,
        make_relation(
            {
                "trip_id": ["T2", "T3"],
                "route_id": ["R2", "R3"],
                "service_id": ["SV2", "SV2"],
            }
        ),
    )
    assert relations_equal(
        filtered_gtfs.stops,
        make_relation({"stop_id": ["S2"], "stop_name": ["Stop 2"]}),
    )


def test_filter_by_agency_id__when_agency_id_is_unknown__returns_empty_routes(
    sample_gtfs,
):
    filtered_gtfs = filter_by_agency_id(sample_gtfs, ["UNKNOWN"])

    assert is_empty(filtered_gtfs.routes)
    assert is_empty(filtered_gtfs.trips)
    assert is_empty(filtered_gtfs.stop_times)


def test_filter_by_agency_id__when_single_agency_without_agency_id_in_routes__keeps_all_routes(
    single_agency_gtfs,
):
    filtered_gtfs = filter_by_agency_id(single_agency_gtfs, ["A"])

    assert relations_equal(filtered_gtfs.routes, single_agency_gtfs.routes)
    assert relations_equal(filtered_gtfs.trips, single_agency_gtfs.trips)


def test_filter_by_agency_id__when_single_agency_without_agency_id_in_routes_and_unknown_agency__returns_empty_routes(
    single_agency_gtfs,
):
    filtered_gtfs = filter_by_agency_id(single_agency_gtfs, ["UNKNOWN"])

    assert is_empty(filtered_gtfs.routes)
    assert is_empty(filtered_gtfs.trips)
