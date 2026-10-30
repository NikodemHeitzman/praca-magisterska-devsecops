"""Shared fixtures: PostgreSQL test database (ADR-0011), in-process S3 (ADR-0012), API client.

Requires the db service from compose.yaml (docker compose up -d db). The test database is
TEST_DATABASE_URL, or DATABASE_URL from .env with the database name suffixed with _test.

The tests check behaviour, not the properties the catalog patches change (GT-03, GT-06,
GT-13, GT-18...GT-20 and others): every patch must pass them (experiment/PROTOCOL.md).
"""

import os
import secrets
import tempfile
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import TYPE_CHECKING

import boto3
import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from moto import mock_aws
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.orm import Session

if TYPE_CHECKING:
    from ticketing.models import User

APP_DIR = Path(__file__).resolve().parent.parent
AWS_REGION = "eu-central-1"
TEST_BUCKET = "test-attachments"
# Generated per run, so that no password literal sits in the repository.
TEST_PASSWORD = secrets.token_urlsafe(16)

# ticketing.main reads the settings once at import, so the environment comes first.
os.environ.update(
    {
        "JWT_SECRET": secrets.token_urlsafe(48),
        "S3_BUCKET": TEST_BUCKET,
        # Empty: boto3 talks to "real" S3, which mock_aws intercepts.
        "S3_ENDPOINT_URL": "",
        "ATTACHMENT_CACHE_DIR": tempfile.mkdtemp(prefix="ticketing-test-cache-"),
        # Fake credentials, so that nothing can reach a real AWS account.
        "AWS_ACCESS_KEY_ID": "testing",
        "AWS_SECRET_ACCESS_KEY": "testing",
        "AWS_SESSION_TOKEN": "testing",
        "AWS_DEFAULT_REGION": AWS_REGION,
    }
)


def _test_database_url() -> URL:
    from ticketing.config import Settings

    if explicit := os.environ.get("TEST_DATABASE_URL"):
        url = make_url(explicit)
    else:
        url = make_url(Settings().database_url)
        url = url.set(database=f"{url.database}_test")
    # The database is dropped at the start of every run; never point it at real data.
    if not (url.database or "").endswith("_test"):
        raise RuntimeError(f"Test database name must end with _test, got {url.database!r}")
    return url


TEST_DATABASE_URL = _test_database_url()
os.environ["DATABASE_URL"] = TEST_DATABASE_URL.render_as_string(hide_password=False)


@pytest.fixture(scope="session", autouse=True)
def database() -> Iterator[None]:
    """Fresh test database per run, schema built by the Alembic migrations."""
    admin_engine = create_engine(
        TEST_DATABASE_URL.set(database="postgres"), isolation_level="AUTOCOMMIT"
    )
    name = TEST_DATABASE_URL.database
    with admin_engine.connect() as conn:
        conn.execute(text(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)'))
        conn.execute(text(f'CREATE DATABASE "{name}"'))
    admin_engine.dispose()

    # No ini file: alembic.ini would reconfigure logging and disable the app loggers.
    config = Config()
    config.set_main_option("script_location", str(APP_DIR / "migrations"))
    command.upgrade(config, "head")

    yield

    from ticketing.db import get_engine

    get_engine().dispose()


@pytest.fixture(autouse=True)
def clean_tables() -> Iterator[None]:
    yield
    from ticketing.db import get_engine

    with get_engine().begin() as conn:
        conn.execute(text("TRUNCATE attachments, tickets, users RESTART IDENTITY CASCADE"))


@pytest.fixture(autouse=True)
def s3() -> Iterator[object]:
    """Empty in-process S3 with the attachments bucket, separate for every test."""
    with mock_aws():
        client = boto3.client("s3", region_name=AWS_REGION)
        client.create_bucket(
            Bucket=TEST_BUCKET,
            CreateBucketConfiguration={"LocationConstraint": AWS_REGION},
        )
        yield client


@pytest.fixture
def db_session() -> Iterator[Session]:
    """Session for arranging and checking data directly in the database."""
    from ticketing.db import get_sessionmaker

    with get_sessionmaker()() as session:
        yield session


@pytest.fixture
def client() -> Iterator[TestClient]:
    from ticketing.main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def make_user(db_session: Session) -> Callable[..., "User"]:
    """Create a user with TEST_PASSWORD directly in the database."""
    from ticketing.models import Role, User
    from ticketing.security import hash_password

    password_hash = hash_password(TEST_PASSWORD)

    def _make_user(username: str, role: Role = Role.USER) -> User:
        user = User(
            username=username,
            email=f"{username}@example.com",
            password_hash=password_hash,
            role=role,
        )
        db_session.add(user)
        db_session.commit()
        return user

    return _make_user


@pytest.fixture
def login(client: TestClient) -> Callable[[str], dict[str, str]]:
    """Log in through the API and return the Authorization header."""

    def _login(username: str) -> dict[str, str]:
        response = client.post(
            "/api/auth/login", data={"username": username, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200, response.text
        return {"Authorization": f"Bearer {response.json()['access_token']}"}

    return _login
