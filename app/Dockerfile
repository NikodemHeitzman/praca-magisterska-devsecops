# Container image of the research application (E05-01, docs/adr/0022-obraz-kontenera-aplikacji.md).
# Build context: app/ (docker build -t ticketing app/). Images pinned by digest (AGENTS.md, rule 6).
#
# Catalogue constraints (experiment/ground-truth.yaml):
# - GT-08 replaces the digest in the single "AS base" line below with an older digest of the same tag.
# - GT-09 removes the USER instruction. USER appears only in the final stage on purpose: Checkov
#   CKV_DOCKER_3 and Trivy DS-0002 look at the whole file, so a USER in another stage would hide the patch.

FROM ghcr.io/astral-sh/uv:0.13.6@sha256:af22a52f5eafef3d78e551599d405c02df61919d18028f0cea8eda93bc9986d0 AS uv

FROM python:3.14-slim@sha256:9aaa474097d094040649f2162a627c0049b408f52138d980916788d80f04802f AS base

# ---------------------------------------------------------------- build: dependencies from uv.lock
FROM base AS build

COPY --from=uv /uv /usr/local/bin/uv

# System Python of the base image, no downloads; venv outside the source tree so it can be copied whole.
ENV UV_PYTHON=/usr/local/bin/python3 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app
COPY pyproject.toml uv.lock ./
# --frozen: install exactly uv.lock, fail if it is out of date; --no-dev: runtime dependencies only.
RUN uv sync --frozen --no-dev --no-cache

# ---------------------------------------------------------------- runtime
FROM base AS runtime

ENV PATH="/opt/venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# pip from the base image is not needed at run time (dependencies come from /opt/venv) and its
# vendored libraries (urllib3, msgpack, setuptools) gave scanner findings outside the catalogue
# (ADR-0022). No apt-get upgrade here: it would also update an older base digest and cancel GT-08.
RUN python -m pip uninstall --yes --no-input pip \
    && groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app

WORKDIR /app
# Owned by root and read-only for the app user; the app writes only to /tmp (attachment cache).
COPY --from=build /opt/venv /opt/venv
COPY alembic.ini ./
COPY migrations ./migrations
COPY ticketing ./ticketing

USER 10001:10001

EXPOSE 8000

# /health checks the database too (503 when it is unavailable); urlopen raises on non-2xx.
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4)"]

# Migrations are not run here (ADR-0022): the one-off migrate service in compose.yaml runs them (ADR-0023).
CMD ["uvicorn", "ticketing.main:app", "--host", "0.0.0.0", "--port", "8000"]
