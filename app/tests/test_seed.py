"""Seed script: accounts, tickets and the attachment, repeatable."""

import secrets

import pytest
from fastapi.testclient import TestClient

from ticketing import seed
from ticketing.config import get_settings
from ticketing.storage import get_s3_client

PASSWORDS = {name: secrets.token_urlsafe(16) for name in ("alice", "bob", "admin")}


@pytest.fixture
def seed_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name, password in PASSWORDS.items():
        monkeypatch.setenv(f"SEED_{name.upper()}_PASSWORD", password)


def login(client: TestClient, username: str) -> dict[str, str]:
    response = client.post(
        "/api/auth/login", data={"username": username, "password": PASSWORDS[username]}
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.mark.usefixtures("seed_env")
def test_seed_creates_accounts_tickets_and_attachment(client: TestClient) -> None:
    seed.seed()
    seed.seed()  # repeatable: nothing is duplicated

    alice = login(client, "alice")
    tickets = client.get("/api/tickets", params={"sort": "title", "order": "asc"}, headers=alice)
    assert [t["title"] for t in tickets.json()] == [
        "New monitor for the second desk",
        "VPN connection drops every few minutes",
    ]
    vpn = tickets.json()[1]
    download = client.get(f"/api/tickets/{vpn['id']}/attachments/vpn-client.log", headers=alice)
    assert download.status_code == 200
    assert download.content == seed.ATTACHMENT_CONTENT

    assert len(client.get("/api/tickets", headers=login(client, "bob")).json()) == 1
    users = client.get("/api/admin/users", headers=login(client, "admin")).json()
    assert [(u["username"], u["role"]) for u in users] == [
        ("alice", "user"),
        ("bob", "user"),
        ("admin", "admin"),
    ]


@pytest.mark.usefixtures("seed_env")
def test_seed_creates_bucket_in_local_s3_stand_in(s3, monkeypatch: pytest.MonkeyPatch) -> None:
    bucket = get_settings().s3_bucket
    s3.delete_bucket(Bucket=bucket)
    # An AWS-style endpoint, so that mock_aws still intercepts the calls.
    monkeypatch.setattr(get_settings(), "s3_endpoint_url", "https://s3.eu-central-1.amazonaws.com")
    get_s3_client.cache_clear()

    seed.seed()

    assert s3.head_bucket(Bucket=bucket)["ResponseMetadata"]["HTTPStatusCode"] == 200


def test_seed_requires_passwords(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SEED_ALICE_PASSWORD", raising=False)

    with pytest.raises(SystemExit, match="SEED_ALICE_PASSWORD"):
        seed.seed()
