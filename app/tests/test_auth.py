"""Registration, login and token handling."""

import logging
import secrets
from collections.abc import Callable

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from ticketing.config import get_settings
from ticketing.models import User

ME = "/api/users/me"


def registration(username: str = "carol", email: str = "carol@example.com") -> dict[str, str]:
    return {
        "username": username,
        "email": email,
        "password": secrets.token_urlsafe(16),
        "full_name": "Carol Tester",
    }


def test_register_creates_user_who_can_log_in(client: TestClient) -> None:
    data = registration()

    response = client.post("/api/auth/register", json=data)

    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "carol"
    assert body["email"] == "carol@example.com"
    assert body["role"] == "user"
    assert "password" not in body and "password_hash" not in body

    login = client.post("/api/auth/login", data={"username": "carol", "password": data["password"]})
    assert login.status_code == 200
    assert login.json()["token_type"] == "bearer"


@pytest.mark.parametrize(
    "data",
    [registration(email="other@example.com"), registration(username="other")],
    ids=["same-username", "same-email"],
)
def test_register_rejects_taken_username_or_email(client: TestClient, data: dict[str, str]) -> None:
    assert client.post("/api/auth/register", json=registration()).status_code == 201

    response = client.post("/api/auth/register", json=data)

    assert response.status_code == 409


@pytest.mark.parametrize(
    "changes",
    [{"username": "a b"}, {"email": "not-an-email"}, {"password": "short"}],
    ids=["username", "email", "password"],
)
def test_register_validates_input(client: TestClient, changes: dict[str, str]) -> None:
    response = client.post("/api/auth/register", json=registration() | changes)

    assert response.status_code == 422


def test_login_returns_token_for_current_user(
    client: TestClient,
    make_user: Callable[..., User],
    login: Callable[[str], dict[str, str]],
) -> None:
    make_user("alice")

    response = client.get(ME, headers=login("alice"))

    assert response.status_code == 200
    assert response.json()["username"] == "alice"


@pytest.mark.parametrize("username", ["alice", "nobody"], ids=["wrong-password", "unknown-user"])
def test_login_rejects_bad_credentials_and_logs_attempt(
    client: TestClient,
    make_user: Callable[..., User],
    caplog: pytest.LogCaptureFixture,
    username: str,
) -> None:
    make_user("alice")

    with caplog.at_level(logging.WARNING, logger="ticketing.routers.auth"):
        response = client.post("/api/auth/login", data={"username": username, "password": "wrong"})

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    assert f"Failed login for user {username}" in caplog.text


def test_me_requires_token(client: TestClient) -> None:
    assert client.get(ME).status_code == 401


def test_me_rejects_malformed_token(client: TestClient) -> None:
    response = client.get(ME, headers={"Authorization": "Bearer not-a-jwt"})

    assert response.status_code == 401


def test_me_rejects_expired_token(
    client: TestClient,
    make_user: Callable[..., User],
    login: Callable[[str], dict[str, str]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    make_user("alice")
    monkeypatch.setattr(get_settings(), "jwt_expire_minutes", -1)

    response = client.get(ME, headers=login("alice"))

    assert response.status_code == 401


def test_me_rejects_token_of_deleted_user(
    client: TestClient,
    make_user: Callable[..., User],
    login: Callable[[str], dict[str, str]],
    db_session: Session,
) -> None:
    user = make_user("alice")
    headers = login("alice")
    db_session.delete(user)
    db_session.commit()

    response = client.get(ME, headers=headers)

    assert response.status_code == 401
