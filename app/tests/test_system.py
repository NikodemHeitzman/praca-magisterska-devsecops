"""System endpoints, public pages and security headers."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from ticketing.config import Settings
from ticketing.db import get_db
from ticketing.main import app


def test_health_reports_database_ok(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


def test_health_reports_database_unavailable(client: TestClient) -> None:
    class BrokenSession:
        def execute(self, *args: object) -> None:
            raise OperationalError("SELECT 1", {}, Exception("connection refused"))

    def broken_db() -> Iterator[BrokenSession]:
        yield BrokenSession()

    app.dependency_overrides[get_db] = broken_db
    try:
        response = client.get("/health")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json() == {"status": "degraded", "database": "unavailable"}


@pytest.mark.parametrize("path", ["/", "/login"])
def test_public_pages_send_security_headers(client: TestClient, path: str) -> None:
    response = client.get(path)

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "frame-ancestors 'none'" in response.headers["content-security-policy"]
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["x-content-type-options"] == "nosniff"


def test_docs_use_relaxed_csp(client: TestClient) -> None:
    response = client.get("/docs")

    assert response.status_code == 200
    csp = response.headers["content-security-policy"]
    assert "https://cdn.jsdelivr.net" in csp
    assert "frame-ancestors 'none'" in csp


def test_openapi_schema_is_served(client: TestClient) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["title"] == "Ticketing"


def test_settings_split_comma_separated_lists() -> None:
    settings = Settings(
        cors_origins="http://a.test, http://b.test,", allowed_content_types="text/plain"
    )

    assert settings.cors_origins == ["http://a.test", "http://b.test"]
    assert settings.allowed_content_types == ["text/plain"]


def test_settings_treat_empty_s3_endpoint_as_real_s3() -> None:
    assert Settings(s3_endpoint_url="").s3_endpoint_url is None
