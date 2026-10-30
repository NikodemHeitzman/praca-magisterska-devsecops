"""Profile of the current user and user administration."""

from collections.abc import Callable

import pytest
from fastapi.testclient import TestClient

from ticketing.models import Role, User

ME = "/api/users/me"


def test_update_profile_changes_given_fields_only(
    client: TestClient,
    make_user: Callable[..., User],
    login: Callable[[str], dict[str, str]],
) -> None:
    make_user("alice")
    headers = login("alice")

    response = client.patch(ME, json={"full_name": "Alice Example"}, headers=headers)

    assert response.status_code == 200
    assert response.json()["full_name"] == "Alice Example"
    assert response.json()["email"] == "alice@example.com"

    response = client.patch(ME, json={"email": "alice.new@example.com"}, headers=headers)

    assert response.status_code == 200
    assert client.get(ME, headers=headers).json() | {"created_at": None} == {
        "id": 1,
        "username": "alice",
        "email": "alice.new@example.com",
        "full_name": "Alice Example",
        "role": "user",
        "created_at": None,
    }


@pytest.mark.parametrize(
    "data", [{"email": None}, {"email": "not-an-email"}], ids=["null", "invalid"]
)
def test_update_profile_validates_email(
    client: TestClient,
    make_user: Callable[..., User],
    login: Callable[[str], dict[str, str]],
    data: dict[str, str | None],
) -> None:
    make_user("alice")

    response = client.patch(ME, json=data, headers=login("alice"))

    assert response.status_code == 422


def test_update_profile_rejects_taken_email(
    client: TestClient,
    make_user: Callable[..., User],
    login: Callable[[str], dict[str, str]],
) -> None:
    make_user("alice")
    make_user("bob")

    response = client.patch(ME, json={"email": "bob@example.com"}, headers=login("alice"))

    assert response.status_code == 409


def test_admin_lists_users(
    client: TestClient,
    make_user: Callable[..., User],
    login: Callable[[str], dict[str, str]],
) -> None:
    make_user("admin", role=Role.ADMIN)
    make_user("alice")

    response = client.get("/api/admin/users", headers=login("admin"))

    assert response.status_code == 200
    assert [(u["username"], u["role"]) for u in response.json()] == [
        ("admin", "admin"),
        ("alice", "user"),
    ]


def test_admin_changes_role(
    client: TestClient,
    make_user: Callable[..., User],
    login: Callable[[str], dict[str, str]],
) -> None:
    make_user("admin", role=Role.ADMIN)
    alice = make_user("alice")

    response = client.patch(
        f"/api/admin/users/{alice.id}/role", json={"role": "admin"}, headers=login("admin")
    )

    assert response.status_code == 200
    assert response.json()["role"] == "admin"


def test_admin_role_change_for_unknown_user_returns_404(
    client: TestClient,
    make_user: Callable[..., User],
    login: Callable[[str], dict[str, str]],
) -> None:
    make_user("admin", role=Role.ADMIN)

    response = client.patch(
        "/api/admin/users/999/role", json={"role": "admin"}, headers=login("admin")
    )

    assert response.status_code == 404


# Role change only; GET /api/admin/users is GT-19 and is not checked for non-admins.
def test_role_change_requires_admin(
    client: TestClient,
    make_user: Callable[..., User],
    login: Callable[[str], dict[str, str]],
) -> None:
    alice = make_user("alice")

    response = client.patch(
        f"/api/admin/users/{alice.id}/role", json={"role": "admin"}, headers=login("alice")
    )

    assert response.status_code == 403
