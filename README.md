# gtfs-filtering

Filter a [GTFS](https://gtfs.org/documentation/schedule/reference/) feed by route ID or trip ID. Available as both a CLI tool and a desktop GUI application.

## Features

- Filter by **route ID**: keeps all trips, stop times, shapes, calendars, etc. linked to the selected routes
- Filter by **trip ID**: resolves to the parent routes then applies the same full filtering
- Reads and writes standard zipped GTFS archives
- Built on [DuckDB](https://duckdb.org/) for fast in-memory SQL filtering

## Requirements

- Python ≥ 3.11
- [uv](https://docs.astral.sh/uv/)

## Installation

```bash
uv sync
```

## Usage

### CLI

```bash
uv run python -m gtfs_filtering.cli INPUT_GTFS_ZIP OUTPUT_GTFS_ZIP FILTER_VALUE...
```

**Options**

| Option | Default | Description |
|---|---|---|
| `-t`, `--filter-type` | `route_id` | `route_id` or `trip_id` |
| `-o`, `--overwrite` | off | Overwrite output file if it already exists |

**Examples**

```bash
# Filter by route IDs 1, 2 and 3
uv run python -m gtfs_filtering.cli input.zip output.zip 1 2 3

# Filter by trip ID
uv run python -m gtfs_filtering.cli --filter-type trip_id input.zip output.zip TRIP_ID_1

# Overwrite existing output
uv run python -m gtfs_filtering.cli -o input.zip output.zip 1 2 3
```

### GUI

```bash
uv run python -m gtfs_filtering.gui
```

## Development

### Install all dependencies (including dev)

```bash
make install-all-deps
```

### Lint & format

```bash
make lint-check      # check only
make lint            # auto-fix
make format-check    # check only
make format          # auto-fix
```

### Tests

```bash
make unit            # unit tests
make e2e             # end-to-end tests (requires packaged CLI)
make tests           # both
```

### Build standalone binaries

```bash
make package-cli     # produces dist/cli
make package-gui     # produces dist/gui
```

### Dependency management

```bash
make update-deps     # upgrade to latest versions
make check-deps      # audit for vulnerabilities
```

### Clean

```bash
make clean
```
