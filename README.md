# gtfs-filtering

Filter a [GTFS](https://gtfs.org/documentation/schedule/reference/) feed by route ID or trip ID. Available as a CLI tool, a desktop GUI application and a web API.

## Features

- Filter by **route ID**: keeps all trips, stop times, shapes, calendars, etc. linked to the selected routes
- Filter by **trip ID**: resolves to the parent routes then applies the same full filtering
- Reads and writes standard zipped GTFS archives
- Built on [DuckDB](https://duckdb.org/) for fast in-memory SQL filtering

## Requirements

- Python ≥ 3.11
- [uv](https://docs.astral.sh/uv/)

## Installation

Dependencies are split by entrypoint: the CLI, the GUI and the web API each have their own extra on top of the shared base dependencies.

```bash
uv sync --extra cli      # CLI (click)
uv sync --extra gui      # GUI (PyQt6)
uv sync --extra web      # web API (FastAPI)
```

## Usage

### CLI

```bash
uv run --extra cli python -m gtfs_filtering.cli INPUT_GTFS_ZIP OUTPUT_GTFS_ZIP FILTER_VALUE...
```

**Options**

| Option | Default | Description |
|---|---|---|
| `-t`, `--filter-type` | `route_id` | `route_id` or `trip_id` |
| `-o`, `--overwrite` | off | Overwrite output file if it already exists |

**Examples**

```bash
# Filter by route IDs 1, 2 and 3
uv run --extra cli python -m gtfs_filtering.cli input.zip output.zip 1 2 3

# Filter by trip ID
uv run --extra cli python -m gtfs_filtering.cli --filter-type trip_id input.zip output.zip TRIP_ID_1

# Overwrite existing output
uv run --extra cli python -m gtfs_filtering.cli -o input.zip output.zip 1 2 3
```

### GUI

```bash
uv run --extra gui python -m gtfs_filtering.gui
```

### Web API

Built with [FastAPI](https://fastapi.tiangolo.com/).

```bash
make web                                                                # server on port 8000
uv run --extra web uvicorn gtfs_filtering.web.main:app --reload           # development server with auto-reload
```

Interactive documentation is served at `http://localhost:8000/docs`.

**Docker**

```bash
docker build -t gtfs-filtering-web .
docker run -p 8000:8000 gtfs-filtering-web
docker run -p 8000:8000 -e GTFS_FILTERING_MAX_UPLOAD_SIZE_MB=500 gtfs-filtering-web   # override settings
```

**Endpoints**

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness probe |
| `POST` | `/api/v1/filter` | Filters an uploaded GTFS zip, returns the filtered GTFS zip |

`POST /api/v1/filter` takes a `multipart/form-data` body:

| Field | Required | Description |
|---|---|---|
| `gtfs_zip` | yes | GTFS zip to filter |
| `filter_values` | yes | Value to keep, repeat the field for several values |
| `filter_type` | no | `route_id` (default) or `trip_id` |

```bash
curl -F gtfs_zip=@input.zip -F filter_values=1 -F filter_values=2 \
     -o output.zip http://localhost:8000/api/v1/filter
```

**Configuration** (environment variables or `.env` file)

| Variable | Default | Description |
|---|---|---|
| `GTFS_FILTERING_MAX_UPLOAD_SIZE_MB` | `200` | Maximum size of uploaded GTFS zip (413 returned above) |
| `GTFS_FILTERING_MAX_UNCOMPRESSED_SIZE_MB` | `2048` | Maximum total uncompressed size of uploaded GTFS zip (413 returned above) |
| `GTFS_FILTERING_MAX_ARCHIVE_ENTRIES` | `100` | Maximum number of files in uploaded GTFS zip (413 returned above) |
| `GTFS_FILTERING_MAX_COMPRESSION_RATIO` | `100` | Maximum compression ratio of a single file in uploaded GTFS zip (413 returned above) |

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
make cli     # produces dist/cli
make gui     # produces dist/gui
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
