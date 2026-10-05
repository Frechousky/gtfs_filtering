# syntax=docker/dockerfile:1

# build stage: install dependencies into a virtual environment with uv
# uses Debian 12 system python so the virtual environment matches distroless runtime python (/usr/bin/python3.11)
FROM debian:bookworm-slim AS builder

RUN apt-get update \
    && apt-get install --yes --no-install-recommends python3 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.11 /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON=/usr/bin/python3.11 \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev --extra web

# runtime stage: distroless python (no shell, no package manager), runs as non-root user
FROM gcr.io/distroless/python3-debian12:nonroot

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
# web API sources only (CLI and GUI entrypoints are not shipped)
COPY gtfs_filtering/__init__.py gtfs_filtering/core.py ./gtfs_filtering/
COPY gtfs_filtering/web ./gtfs_filtering/web

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["/app/.venv/bin/python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]

ENTRYPOINT ["/app/.venv/bin/python", "-m", "uvicorn"]
CMD ["gtfs_filtering.web.main:app", "--host", "0.0.0.0", "--port", "8000"]
