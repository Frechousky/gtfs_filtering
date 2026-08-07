#!/usr/bin/env python3
import csv
import dataclasses
import enum
import logging
import os
import shutil
import typing
import zipfile

import duckdb

_IS_WINDOWS = os.name == "nt"  # check if user OS is WINDOWS
_ZIP_EXTRACT_TMP = (
    os.path.join("C:\\", "temp", "gtfs-utils-zip_extract_tmp")
    if _IS_WINDOWS
    else os.path.join("/tmp", "gtfs-utils-zip_extract_tmp")
)


class EmptyDataError(ValueError):
    pass


@dataclasses.dataclass
class GTFS:
    """
    Stores static GTFS data

    Each field stores data from a single GTFS file, e.g. 'agency' field stores data from GTFS file 'agency.txt'
    """

    agency: typing.Optional[duckdb.DuckDBPyRelation] = None
    stops: typing.Optional[duckdb.DuckDBPyRelation] = None
    routes: typing.Optional[duckdb.DuckDBPyRelation] = None
    trips: typing.Optional[duckdb.DuckDBPyRelation] = None
    stop_times: typing.Optional[duckdb.DuckDBPyRelation] = None  # optional
    calendar: typing.Optional[duckdb.DuckDBPyRelation] = None  # optional
    calendar_dates: typing.Optional[duckdb.DuckDBPyRelation] = None  # optional
    fare_attributes: typing.Optional[duckdb.DuckDBPyRelation] = None  # optional
    fare_rules: typing.Optional[duckdb.DuckDBPyRelation] = None  # optional
    fare_media: typing.Optional[duckdb.DuckDBPyRelation] = None  # optional
    fare_products: typing.Optional[duckdb.DuckDBPyRelation] = None  # optional
    fare_leg_rules: typing.Optional[duckdb.DuckDBPyRelation] = None  # optional
    fare_transfer_rules: typing.Optional[duckdb.DuckDBPyRelation] = None  # optional
    areas: typing.Optional[duckdb.DuckDBPyRelation] = None  # optional
    stop_areas: typing.Optional[duckdb.DuckDBPyRelation] = None  # optional
    shapes: typing.Optional[duckdb.DuckDBPyRelation] = None  # optional
    frequencies: typing.Optional[duckdb.DuckDBPyRelation] = None  # optional
    transfers: typing.Optional[duckdb.DuckDBPyRelation] = None  # optional
    pathways: typing.Optional[duckdb.DuckDBPyRelation] = None  # optional
    levels: typing.Optional[duckdb.DuckDBPyRelation] = None  # optional
    translations: typing.Optional[duckdb.DuckDBPyRelation] = None  # optional
    feed_info: typing.Optional[duckdb.DuckDBPyRelation] = None  # optional
    attributions: typing.Optional[duckdb.DuckDBPyRelation] = None  # optional


OPTIONAL_GTFS_FILES = [
    "stop_times.txt",
    "calendar.txt",
    "calendar_dates.txt",
    "fare_attributes.txt",
    "fare_rules.txt",
    "fare_media.txt",
    "fare_products.txt",
    "fare_leg_rules.txt",
    "fare_transfer_rules.txt",
    "areas.txt",
    "stop_areas.txt",
    "shapes.txt",
    "frequencies.txt",
    "transfers.txt",
    "pathways.txt",
    "levels.txt",
    "translations.txt",
    "feed_info.txt",
    "attributions.txt",
]


def parse_gtfs_file(directory: str, filename: str) -> duckdb.DuckDBPyRelation:
    """
    Parses a single GTFS file from a directory

    Directory is an unzipped GTFS

    Args:
        directory: directory containing GTFS file
        filename: GTFS file to parse

    Returns:
        parsed GTFS file

    Raises:
        FileNotFoundError when directory does not exist
        FileNotFoundError when filename does not exist
        EmptyDataError when file content is empty
    """
    filepath = os.path.join(directory, filename)
    with open(filepath, "r") as f:
        first_char = f.read(1)
    if not first_char:
        raise EmptyDataError(f"No columns to parse from file '{filename}'.")
    return duckdb.read_csv(filepath, all_varchar=True)


def parse_gtfs(directory: str) -> GTFS:
    """
    Parses all GTFS files from a directory

    Parses all required AND optional GTFS files (according to GTFS spec)
    Ignores missing optional GTFS files
    Directory is an unzipped GTFS

    Args:
        directory: directory to parses GTFS files from

    Returns:
        Parsed GTFS files

    Raises:
        FileNotFoundError when a required GTFS file is missing
    """
    try:
        # required files in GTFS archive
        agency = parse_gtfs_file(directory, "agency.txt")
        stops = parse_gtfs_file(directory, "stops.txt")
        routes = parse_gtfs_file(directory, "routes.txt")
        trips = parse_gtfs_file(directory, "trips.txt")
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"GTFS is invalid: file '{os.path.basename(e.filename)}' is missing."
        )
    gtfs = GTFS(agency=agency, stops=stops, routes=routes, trips=trips)
    # load optional files
    for gtfs_file in OPTIONAL_GTFS_FILES:
        try:
            optional_file_content = parse_gtfs_file(directory, gtfs_file)
            attr_name = gtfs_file.rstrip(".txt")
            gtfs.__setattr__(attr_name, optional_file_content)
        except FileNotFoundError:
            # optional files may be missing
            pass
        except EmptyDataError:
            logging.warning(f"File {gtfs_file} is present but empty, ignores it")

    return gtfs


def save_gtfs(gtfs: GTFS, directory: str) -> None:
    """
    Saves all GTFS file into a directory

    This will generate an unzipped GTFS
    Only non-None files will be saved

    Args:
        gtfs: GTFS files to save
        directory: directory to save GTFS

    Returns:
        None

    Raises:
        OSError when directory does not exist
        PermissionError when directory is not writable
    """
    for field in dataclasses.fields(gtfs):
        gtfs_data: duckdb.DuckDBPyRelation = gtfs.__getattribute__(field.name)
        if gtfs_data is not None:
            output_path = os.path.join(directory, f"{field.name}.txt")
            columns = gtfs_data.columns
            rows = gtfs_data.fetchall()
            with open(output_path, "w", newline="") as f:
                writer = csv.writer(f, lineterminator="\n")
                writer.writerow(columns)
                writer.writerows(rows)


def filter_by_column_values(
    rel: duckdb.DuckDBPyRelation, col_name: str, accepted_values: typing.List[str]
) -> duckdb.DuckDBPyRelation:
    """
    Filters a relation by column such as a SQL 'IN' filtering

    Keep rows with value in accepted values
    (discard rows with empty or different value)

    Args:
        rel: relation to filter
        col_name: column to filter
        accepted_values: values to keep

    Returns:
        Filtered relation

    Raises:
        KeyError when column is not in relation
    """
    if col_name not in rel.columns:
        raise KeyError(col_name)
    if not accepted_values:
        return rel.filter("1=0")
    escaped = [str(v).replace("'", "''") for v in accepted_values]
    values_str = ", ".join(f"'{v}'" for v in escaped)
    return rel.filter(f'"{col_name}" IN ({values_str})')


def filter_by_column_values_optional(
    rel: duckdb.DuckDBPyRelation, col_name: str, accepted_values: typing.List[str]
) -> duckdb.DuckDBPyRelation:
    """
    Filters a relation by an optional column such as a SQL 'IN' filtering

    When column does not exist, do nothing
    When column exists, keep rows with value in accepted values or with an empty value
    (discard rows with different values ONLY)

    Args:
        rel: relation to filter
        col_name: column to filter
        accepted_values: values to keep

    Returns:
        Filtered relation
    """
    if col_name not in rel.columns:
        return rel
    if not accepted_values:
        return rel.filter(f'"{col_name}" IS NULL')
    escaped = [str(v).replace("'", "''") for v in accepted_values]
    values_str = ", ".join(f"'{v}'" for v in escaped)
    return rel.filter(f'"{col_name}" IN ({values_str}) OR "{col_name}" IS NULL')


def get_unique_not_null_column_values(
    rel: duckdb.DuckDBPyRelation, col_name: str
) -> typing.List[str]:
    """
    Retrieves all distinct not-null values from a relation column

    Similar to SQL 'SELECT distinct(col_name) FROM rel WHERE col_name IS NOT NULL'

    Args:
        rel: relation to retrieves unique values of
        col_name: relation's column to retrieves unique values of

    Returns:
        All distinct values from a relation column

    Raises:
        KeyError when column is not in relation
    """
    if col_name not in rel.columns:
        raise KeyError(col_name)
    result = rel.select(f'"{col_name}"').filter(f'"{col_name}" IS NOT NULL').distinct()
    return [row[0] for row in result.fetchall()]


def filter_by_route_id(gtfs_in: GTFS, route_ids: typing.List[str]) -> GTFS:
    """
    Filters all GTFS files by route id

    Args:
        gtfs_in: parsed GTFS input
        route_ids: route ids to keep

    Returns:
        Filtered GTFS by route id
    """
    agency = gtfs_in.agency
    stops = gtfs_in.stops
    routes = gtfs_in.routes
    trips = gtfs_in.trips
    stop_times = gtfs_in.stop_times
    calendar = gtfs_in.calendar
    calendar_dates = gtfs_in.calendar_dates
    areas = gtfs_in.areas
    stop_areas = gtfs_in.stop_areas
    shapes = gtfs_in.shapes
    frequencies = gtfs_in.frequencies
    transfers = gtfs_in.transfers
    pathways = gtfs_in.pathways
    levels = gtfs_in.levels
    attributions = gtfs_in.attributions

    routes = filter_by_column_values(routes, "route_id", route_ids)
    agency_ids = get_unique_not_null_column_values(routes, "agency_id")

    if len(agency_ids):
        # agency_id is not mandatory in routes.txt, make sure there is at least one non-null agency_id
        agency = filter_by_column_values(agency, "agency_id", agency_ids)

    trips = filter_by_column_values(trips, "route_id", route_ids)
    trip_ids = get_unique_not_null_column_values(trips, "trip_id")

    stop_times = filter_by_column_values(stop_times, "trip_id", trip_ids)
    stop_ids_from_stop_times = get_unique_not_null_column_values(stop_times, "stop_id")
    if "parent_station" in stops:
        filtered_stops = filter_by_column_values(
            stops, "stop_id", stop_ids_from_stop_times
        )
        filtered_stops_parent_stations = filtered_stops.filter(
            "length(parent_station) > 0"
        )
        stop_ids_from_parent_stations = [
            row[0]
            for row in filtered_stops_parent_stations.select('"parent_station"')
            .distinct()
            .fetchall()
        ]
        stop_ids = list(set(stop_ids_from_stop_times + stop_ids_from_parent_stations))
    else:
        stop_ids = set(stop_ids_from_stop_times)
    stops = filter_by_column_values(stops, "stop_id", stop_ids)

    service_ids = get_unique_not_null_column_values(trips, "service_id")
    if calendar is not None:
        # optional file
        calendar = filter_by_column_values(calendar, "service_id", service_ids)
    if calendar_dates is not None:
        # optional file
        calendar_dates = filter_by_column_values(
            calendar_dates, "service_id", service_ids
        )

    if areas is not None and stop_areas is not None:
        # optional files
        stop_areas = filter_by_column_values(stop_areas, "stop_id", stop_ids)
        area_ids = get_unique_not_null_column_values(stop_areas, "area_id")
        areas = filter_by_column_values(areas, "area_id", area_ids)

    if shapes is not None:
        # optional file
        shape_ids = get_unique_not_null_column_values(trips, "shape_id")
        if len(shape_ids):
            shapes = filter_by_column_values(shapes, "shape_id", shape_ids)

    if frequencies is not None:
        # optional file
        frequencies = filter_by_column_values(frequencies, "trip_id", trip_ids)

    if transfers is not None:
        # optional file
        transfers = filter_by_column_values(transfers, "from_stop_id", stop_ids)
        transfers = filter_by_column_values(transfers, "to_stop_id", stop_ids)
        transfers = filter_by_column_values_optional(
            transfers, "from_route_id", route_ids
        )
        transfers = filter_by_column_values_optional(
            transfers, "to_route_id", route_ids
        )
        transfers = filter_by_column_values_optional(
            transfers, "from_trip_id", trip_ids
        )
        transfers = filter_by_column_values_optional(transfers, "to_trip_id", trip_ids)

    if pathways is not None:
        # optional file
        pathways = filter_by_column_values(pathways, "from_stop_id", stop_ids)
        pathways = filter_by_column_values(pathways, "to_stop_id", stop_ids)

    if levels is not None:
        # optional file
        level_ids = get_unique_not_null_column_values(stops, "level_id")
        if len(level_ids):
            levels = filter_by_column_values(levels, "level_id", level_ids)

    if attributions is not None:
        # optional file
        attributions = filter_by_column_values_optional(
            attributions, "agency_id", agency_ids
        )
        attributions = filter_by_column_values_optional(
            attributions, "route_id", route_ids
        )
        attributions = filter_by_column_values_optional(
            attributions, "trip_id", trip_ids
        )

    # TODO check if there is filtering to perform by routes.network_id

    return GTFS(
        agency=agency,
        stops=stops,
        routes=routes,
        trips=trips,
        stop_times=stop_times,
        calendar=calendar,
        calendar_dates=calendar_dates,
        areas=areas,
        stop_areas=stop_areas,
        shapes=shapes,
        frequencies=frequencies,
        transfers=transfers,
        pathways=pathways,
        levels=levels,
        attributions=attributions,
    )


def filter_by_trip_id(gtfs_in: GTFS, trip_ids: typing.List[str]) -> GTFS:
    """
    Filters all GTFS files by trip id

    Args:
        gtfs_in: parsed GTFS input
        trip_ids: trip ids to keep

    Returns:
        Filtered GTFS by trip id
    """
    trips = gtfs_in.trips
    filtered_trips = filter_by_column_values(trips, "trip_id", trip_ids)
    route_ids = get_unique_not_null_column_values(filtered_trips, "route_id")
    gtfs_in.trips = filtered_trips
    return filter_by_route_id(gtfs_in, route_ids)


class FilterType(enum.StrEnum):
    ROUTE_ID = "route_id"
    TRIP_ID = "trip_id"


def perform_filter(
    input_gtfs_zip: str,
    output_gtfs_zip: str,
    filter_type: FilterType,
    filter_values: typing.List[str],
    overwrite_output_gtfs: bool,
) -> None:
    """
    Unzip input_gtfs_zip, parse and filter it by route_id or trip_id.
    Filtered GTFS is zipped in output_gtfs_zip.
    Clean all files generated except output_gtfs_zip.

    Args:
        input_gtfs_zip: fullpath GTFS zip to filter
        output_gtfs_zip: fullpath to filtered GTFS zip
        filter_type: type of filtering to perform
        filter_values: values to keep (values not in filter_values are discarded)
        overwrite_output_gtfs: flag to overwrite output_gtfs_zip if it already exists

    Raises:
        FileExistsError when overwrite_output_gtfs is False and output_gtfs_zip already exists
        FileNotFoundError when a required GTFS file is missing
        PermissionError when output directory is not writable
        ValueError when filter type is invalid
    """
    if os.path.isfile(output_gtfs_zip) and not overwrite_output_gtfs:
        raise FileExistsError(f"File '{output_gtfs_zip}' already exists.")
    try:
        os.makedirs(_ZIP_EXTRACT_TMP, exist_ok=True)
        zipfile.ZipFile(input_gtfs_zip).extractall(_ZIP_EXTRACT_TMP)
        gtfs = parse_gtfs(_ZIP_EXTRACT_TMP)
        match filter_type:
            case FilterType.ROUTE_ID:
                gtfs = filter_by_route_id(gtfs, filter_values)
            case FilterType.TRIP_ID:
                gtfs = filter_by_trip_id(gtfs, filter_values)
            case _:
                raise ValueError(f"Invalid filter type {filter_type}.")
        save_gtfs(gtfs, _ZIP_EXTRACT_TMP)
        shutil.make_archive(output_gtfs_zip.rstrip(".zip"), "zip", _ZIP_EXTRACT_TMP)
    finally:
        shutil.rmtree(_ZIP_EXTRACT_TMP, ignore_errors=True)
