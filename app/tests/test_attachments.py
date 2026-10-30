"""Attachments: upload to S3, download through the local cache, removal with the ticket.

Not checked here, because the GT-05 patch changes it: names that leave the cache directory.
"""

from collections.abc import Callable
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ticketing.config import get_settings
from ticketing.models import User

Headers = dict[str, str]


@pytest.fixture
def alice(make_user: Callable[..., User], login: Callable[[str], Headers]) -> Headers:
    make_user("alice")
    return login("alice")


@pytest.fixture
def ticket_url(client: TestClient, alice: Headers) -> str:
    response = client.post("/api/tickets", json={"title": "Printer jam"}, headers=alice)
    return f"/api/tickets/{response.json()['id']}"


def upload(
    client: TestClient,
    url: str,
    headers: Headers,
    name: str = "report.txt",
    content: bytes = b"paper jam in tray 2\n",
    content_type: str = "text/plain",
):
    return client.post(
        f"{url}/attachments", files={"file": (name, content, content_type)}, headers=headers
    )


def test_upload_stores_object_in_s3(
    client: TestClient, alice: Headers, ticket_url: str, s3
) -> None:
    response = upload(client, ticket_url, alice)

    assert response.status_code == 201
    body = response.json()
    assert body["filename"] == "report.txt"
    assert body["content_type"] == "text/plain"
    assert body["size"] == 20
    stored = s3.get_object(Bucket=get_settings().s3_bucket, Key="tickets/1/report.txt")
    assert stored["Body"].read() == b"paper jam in tray 2\n"

    listed = client.get(f"{ticket_url}/attachments", headers=alice).json()
    detail = client.get(ticket_url, headers=alice).json()
    assert [a["filename"] for a in listed] == ["report.txt"]
    assert [a["filename"] for a in detail["attachments"]] == ["report.txt"]


@pytest.mark.parametrize(
    ("raw", "cleaned"),
    [("C:\\Users\\alice\\report v1.txt", "report_v1.txt"), ("docs/notes/zażółć.txt", "za____.txt")],
    ids=["windows-path", "unicode"],
)
def test_upload_keeps_clean_base_name(
    client: TestClient, alice: Headers, ticket_url: str, raw: str, cleaned: str
) -> None:
    response = upload(client, ticket_url, alice, name=raw)

    assert response.status_code == 201
    assert response.json()["filename"] == cleaned


def test_upload_rejects_name_without_file_part(
    client: TestClient, alice: Headers, ticket_url: str
) -> None:
    assert upload(client, ticket_url, alice, name="..").status_code == 422


def test_upload_rejects_disallowed_type(
    client: TestClient, alice: Headers, ticket_url: str
) -> None:
    response = upload(client, ticket_url, alice, name="page.html", content_type="text/html")

    assert response.status_code == 415


def test_upload_rejects_too_large_file(
    client: TestClient, alice: Headers, ticket_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(get_settings(), "max_upload_bytes", 10)

    assert upload(client, ticket_url, alice, content=b"x" * 11).status_code == 413


def test_upload_rejects_duplicate_name(client: TestClient, alice: Headers, ticket_url: str) -> None:
    assert upload(client, ticket_url, alice).status_code == 201

    assert upload(client, ticket_url, alice).status_code == 409


def test_upload_requires_access_to_ticket(
    client: TestClient,
    ticket_url: str,
    make_user: Callable[..., User],
    login: Callable[[str], Headers],
) -> None:
    make_user("bob")

    assert upload(client, ticket_url, login("bob")).status_code == 404


def test_download_fetches_from_s3_then_serves_cached_copy(
    client: TestClient, alice: Headers, ticket_url: str, s3, attachment_cache: Path
) -> None:
    upload(client, ticket_url, alice)

    first = client.get(f"{ticket_url}/attachments/report.txt", headers=alice)

    assert first.status_code == 200
    assert first.content == b"paper jam in tray 2\n"
    assert "attachment" in first.headers["content-disposition"]
    assert (attachment_cache / "1" / "report.txt").is_file()

    # Served from the cache even when the object is gone from S3.
    s3.delete_object(Bucket=get_settings().s3_bucket, Key="tickets/1/report.txt")
    second = client.get(f"{ticket_url}/attachments/report.txt", headers=alice)
    assert second.status_code == 200
    assert second.content == first.content


def test_download_unknown_attachment_returns_404(
    client: TestClient, alice: Headers, ticket_url: str
) -> None:
    response = client.get(f"{ticket_url}/attachments/missing.txt", headers=alice)

    assert response.status_code == 404


def test_delete_ticket_removes_objects_and_cache(
    client: TestClient, alice: Headers, ticket_url: str, s3, attachment_cache: Path
) -> None:
    upload(client, ticket_url, alice)
    client.get(f"{ticket_url}/attachments/report.txt", headers=alice)

    assert client.delete(ticket_url, headers=alice).status_code == 204

    assert s3.list_objects_v2(Bucket=get_settings().s3_bucket)["KeyCount"] == 0
    assert not (attachment_cache / "1").exists()
