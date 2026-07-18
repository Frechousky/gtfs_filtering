import os
import typing

import duckdb
import pytest

VALID_GTFS_FILE = "agency.txt"
EMPTY_FILE = "empty.txt"
NOT_EXISTING_FILE = "not_existing.txt"

VALID_GTFS_FILE_CONTENT = """agency_id,agency_name,agency_url,agency_timezone,agency_lang,agency_phone
MTA NYCT,MTA New York City Transit,http://www.mta.info,America/New_York,en,718-330-1234"""


def make_relation(data: typing.Dict[str, typing.List]) -> duckdb.DuckDBPyRelation:
    """Create a DuckDB relation from a dict of {column_name: [values]}. All values cast to VARCHAR."""
    columns = list(data.keys())
    n_rows = len(next(iter(data.values()))) if data else 0

    if n_rows == 0:
        col_defs = ", ".join(f'NULL::VARCHAR AS "{col}"' for col in columns)
        return duckdb.sql(f"SELECT {col_defs} WHERE 1=0")

    col_params = ", ".join(f"c{i}" for i in range(len(columns)))
    col_aliases = ", ".join(
        f'c{i}::VARCHAR AS "{col}"' for i, col in enumerate(columns)
    )

    row_strs = []
    for i in range(n_rows):
        vals = []
        for col in columns:
            v = data[col][i]
            if v is None:
                vals.append("NULL")
            else:
                escaped = str(v).replace("'", "''")
                vals.append(f"'{escaped}'")
        row_strs.append(f"({', '.join(vals)})")

    values_str = ", ".join(row_strs)
    return duckdb.sql(
        f"SELECT {col_aliases} FROM (VALUES {values_str}) AS t({col_params})"
    )


def _sort_key(row: tuple) -> tuple:
    return tuple("" if v is None else str(v) for v in row)


def relations_equal(r1: duckdb.DuckDBPyRelation, r2: duckdb.DuckDBPyRelation) -> bool:
    """Returns True if two relations have the same columns and rows (order-insensitive)."""
    if r1.columns != r2.columns:
        return False
    return sorted(r1.fetchall(), key=_sort_key) == sorted(r2.fetchall(), key=_sort_key)


def is_empty(rel: duckdb.DuckDBPyRelation) -> bool:
    """Returns True if the relation has no rows."""
    return rel.count("*").fetchone()[0] == 0


@pytest.fixture()
def valid_gtfs_file(tmp_path):
    """creates valid GTFS file for testing"""
    filepath = os.path.join(tmp_path, VALID_GTFS_FILE)
    with open(filepath, "w") as f:
        f.write(VALID_GTFS_FILE_CONTENT)


@pytest.fixture()
def empty_gtfs_file(tmp_path):
    """creates an empty file for testing"""
    filepath = os.path.join(tmp_path, EMPTY_FILE)
    with open(filepath, "w") as f:
        f.write("")


@pytest.fixture()
def not_existing_file(tmp_path):
    """deletes file before testing if it exists"""
    filepath = os.path.join(tmp_path, NOT_EXISTING_FILE)
    try:
        os.remove(filepath)
    except FileNotFoundError:
        pass
