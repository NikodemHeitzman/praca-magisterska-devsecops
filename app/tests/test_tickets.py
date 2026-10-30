"""Tickets: CRUD, listing, search and status changes.

Not checked here, because catalog patches change it: access to another user's ticket through
GET /api/tickets/{id} (GT-18), rejection of unknown sort names (GT-04), search input with
SQL syntax (GT-01).
"""

from collections.abc import Callable, Iterator

import pytest
from fastapi.testclient import TestClient

from ticketing.main import app
from ticketing.models import Role, User

TICKETS = "/api/tickets"
Headers = dict[str, str]


@pytest.fixture
def alice(make_user: Callable[..., User], login: Callable[[str], Headers]) -> Headers:
    make_user("alice")
    return login("alice")


@pytest.fixture
def bob(make_user: Callable[..., User], login: Callable[[str], Headers]) -> Headers:
    make_user("bob")
    return login("bob")


@pytest.fixture
def admin(make_user: Callable[..., User], login: Callable[[str], Headers]) -> Headers:
    make_user("admin", role=Role.ADMIN)
    return login("admin")


def create(client: TestClient, headers: Headers, title: str, **fields: str) -> dict:
    response = client.post(TICKETS, json={"title": title, **fields}, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


def titles(response) -> list[str]:
    assert response.status_code == 200, response.text
    return [ticket["title"] for ticket in response.json()]


def test_create_ticket_with_defaults(client: TestClient, alice: Headers) -> None:
    ticket = create(client, alice, "Printer jam")

    assert ticket["status"] == "open"
    assert ticket["priority"] == "medium"
    assert ticket["description"] == ""
    assert ticket["owner_id"] == 1


@pytest.mark.parametrize(
    "data", [{"title": ""}, {"title": "x", "priority": "urgent"}], ids=["empty-title", "priority"]
)
def test_create_ticket_validates_input(client: TestClient, alice: Headers, data: dict) -> None:
    assert client.post(TICKETS, json=data, headers=alice).status_code == 422


def test_list_shows_own_tickets_to_user_and_all_to_admin(
    client: TestClient, alice: Headers, bob: Headers, admin: Headers
) -> None:
    create(client, alice, "Alice ticket")
    create(client, bob, "Bob ticket")

    assert titles(client.get(TICKETS, headers=alice)) == ["Alice ticket"]
    assert sorted(titles(client.get(TICKETS, headers=admin))) == ["Alice ticket", "Bob ticket"]


def test_list_filters_sorts_and_pages(client: TestClient, alice: Headers) -> None:
    create(client, alice, "B", priority="high")
    create(client, alice, "A", priority="low")
    closed = create(client, alice, "C")
    client.post(f"{TICKETS}/{closed['id']}/status", json={"status": "closed"}, headers=alice)

    def listed(**params: str | int) -> list[str]:
        return titles(client.get(TICKETS, params=params, headers=alice))

    assert listed(sort="title", order="asc") == ["A", "B", "C"]
    assert listed(sort="priority", order="desc") == ["B", "C", "A"]
    assert listed(sort="created_at", order="asc") == ["B", "A", "C"]
    assert listed(sort="status", order="asc", status="closed") == ["C"]
    assert listed(sort="title", order="asc", limit=1, offset=1) == ["B"]


def test_search_matches_title_and_description_case_insensitively(
    client: TestClient, alice: Headers, bob: Headers
) -> None:
    create(client, alice, "VPN outage", description="Office network")
    create(client, alice, "Laptop", description="Battery drains after VPN login")
    create(client, alice, "Monitor")
    create(client, bob, "VPN for Bob")

    response = client.get(f"{TICKETS}/search", params={"q": "vpn"}, headers=alice)

    assert titles(response) == ["VPN outage", "Laptop"]


def test_admin_search_covers_all_tickets(
    client: TestClient, alice: Headers, bob: Headers, admin: Headers
) -> None:
    create(client, alice, "VPN outage")
    create(client, bob, "VPN for Bob")

    response = client.get(f"{TICKETS}/search", params={"q": "VPN"}, headers=admin)

    assert titles(response) == ["VPN outage", "VPN for Bob"]


def test_read_ticket_with_attachments(client: TestClient, alice: Headers, admin: Headers) -> None:
    ticket = create(client, alice, "Printer jam")

    for headers in (alice, admin):
        response = client.get(f"{TICKETS}/{ticket['id']}", headers=headers)
        assert response.status_code == 200
        assert response.json()["title"] == "Printer jam"
        assert response.json()["attachments"] == []


def test_read_missing_ticket_returns_404(client: TestClient, alice: Headers) -> None:
    assert client.get(f"{TICKETS}/999", headers=alice).status_code == 404


def test_update_ticket(client: TestClient, alice: Headers) -> None:
    ticket = create(client, alice, "Printer jam", priority="low")

    response = client.patch(
        f"{TICKETS}/{ticket['id']}", json={"priority": "high"}, headers=alice
    )

    assert response.status_code == 200
    assert response.json()["priority"] == "high"
    assert response.json()["title"] == "Printer jam"


def test_update_rejects_null_title(client: TestClient, alice: Headers) -> None:
    ticket = create(client, alice, "Printer jam")

    response = client.patch(f"{TICKETS}/{ticket['id']}", json={"title": None}, headers=alice)

    assert response.status_code == 422


def test_other_user_cannot_change_or_delete_ticket(
    client: TestClient, alice: Headers, bob: Headers
) -> None:
    url = f"{TICKETS}/{create(client, alice, 'Printer jam')['id']}"

    assert client.patch(url, json={"title": "Mine"}, headers=bob).status_code == 404
    assert client.post(f"{url}/status", json={"status": "closed"}, headers=bob).status_code == 404
    assert client.delete(url, headers=bob).status_code == 404


def test_status_follows_allowed_transitions(client: TestClient, alice: Headers) -> None:
    url = f"{TICKETS}/{create(client, alice, 'Printer jam')['id']}/status"

    for new_status in ("in_progress", "resolved", "open", "closed"):
        response = client.post(url, json={"status": new_status}, headers=alice)
        assert response.status_code == 200, response.text
        assert response.json()["status"] == new_status


def test_status_rejects_transition_outside_table(client: TestClient, alice: Headers) -> None:
    url = f"{TICKETS}/{create(client, alice, 'Printer jam')['id']}/status"

    response = client.post(url, json={"status": "resolved"}, headers=alice)

    assert response.status_code == 409


@pytest.fixture
def client_without_raise() -> Iterator[TestClient]:
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


def test_status_change_of_closed_ticket_fails_with_500(
    client_without_raise: TestClient, alice: Headers
) -> None:
    """Deliberate logic error for the GT-14 audit (docs/app-spec.md, section 5).

    Only the status code is checked: the body differs with the GT-14 patch (stack trace).
    """
    client = client_without_raise
    url = f"{TICKETS}/{create(client, alice, 'Printer jam')['id']}/status"
    assert client.post(url, json={"status": "closed"}, headers=alice).status_code == 200

    response = client.post(url, json={"status": "open"}, headers=alice)

    assert response.status_code == 500


def test_delete_ticket(client: TestClient, alice: Headers) -> None:
    url = f"{TICKETS}/{create(client, alice, 'Printer jam')['id']}"

    assert client.delete(url, headers=alice).status_code == 204
    assert client.get(url, headers=alice).status_code == 404
