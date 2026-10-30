"""FastAPI application: middleware and routers."""

import logging
import sys

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import RequestResponseEndpoint

from ticketing.config import get_settings
from ticketing.routers import health, pages

settings = get_settings()

logging.basicConfig(
    stream=sys.stdout,
    level=settings.log_level,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

# No debug argument here (docs/app-spec.md, section 7; GT-14 adds debug=True).
app = FastAPI(title="Ticketing", version="0.1.0")

# CORS through add_middleware, not FastAPI(middleware=[...]): the Semgrep rule for GT-12
# matches this form only. Bearer tokens, no cookies, so no credentials.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

APP_CSP = "default-src 'self'; form-action 'self'; base-uri 'self'; object-src 'none'"
# Swagger UI and ReDoc load their assets from jsDelivr and run an inline bootstrap script.
DOCS_CSP = (
    "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
    "style-src 'self' https://cdn.jsdelivr.net; img-src 'self' data: https://fastapi.tiangolo.com; "
    "worker-src 'self' blob:; base-uri 'self'; object-src 'none'"
)
DOCS_PATHS = {"/docs", "/redoc"}


@app.middleware("http")
async def security_headers(request: Request, call_next: RequestResponseEndpoint) -> Response:
    response = await call_next(request)
    csp = DOCS_CSP if request.url.path in DOCS_PATHS else APP_CSP
    response.headers["Content-Security-Policy"] = f"{csp}; frame-ancestors 'none'"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


app.include_router(health.router)
app.include_router(pages.router)
