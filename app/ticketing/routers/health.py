"""Liveness and database check (Docker HEALTHCHECK, DAST) and the deployed version."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ticketing.config import Settings, get_settings
from ticketing.db import get_db

logger = logging.getLogger(__name__)
router = APIRouter(tags=["system"])


@router.get("/health")
def health(db: Annotated[Session, Depends(get_db)]) -> JSONResponse:
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        logger.warning("Health check: database unavailable")
        return JSONResponse({"status": "degraded", "database": "unavailable"}, status_code=503)
    return JSONResponse({"status": "ok", "database": "ok"})


# Confirms a deployment from outside: the pipeline has no access to the instance (ADR-0033).
# Both values are public anyway (public repository and public GHCR package).
@router.get("/version")
def version(settings: Annotated[Settings, Depends(get_settings)]) -> dict[str, str | None]:
    return {"image": settings.app_image, "revision": settings.app_revision}
