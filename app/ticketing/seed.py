"""Seed data for local runs, the DAST scan and the audit (docs/app-spec.md, section 6).

Run from app/ after the migrations:  uv run --env-file .env python -m ticketing.seed

Idempotent: accounts get the passwords from the environment on every run, missing tickets
are created, and the attachment object is uploaded again (moto keeps data in memory only).
Passwords come from SEED_ALICE_PASSWORD, SEED_BOB_PASSWORD and SEED_ADMIN_PASSWORD, never
from the repository.
"""

import logging
import os
import sys

from botocore.exceptions import ClientError
from sqlalchemy import select
from sqlalchemy.orm import Session

from ticketing import storage
from ticketing.config import get_settings
from ticketing.db import get_sessionmaker
from ticketing.models import Attachment, Role, Ticket, TicketPriority, User
from ticketing.security import hash_password

logger = logging.getLogger("ticketing.seed")

ACCOUNTS = [
    ("alice", "Alice Example", Role.USER),
    ("bob", "Bob Example", Role.USER),
    ("admin", "Administrator", Role.ADMIN),
]

TICKETS = {
    "alice": [
        (
            "VPN connection drops every few minutes",
            "Happens since the client update on Monday.",
            TicketPriority.HIGH,
        ),
        ("New monitor for the second desk", "", TicketPriority.LOW),
    ],
    "bob": [
        ("Printer on the second floor out of toner", "Black toner only.", TicketPriority.MEDIUM),
    ],
}

ATTACHMENT_FILENAME = "vpn-client.log"
ATTACHMENT_CONTENT = (
    b"2026-10-26 09:14:02 INFO tunnel established\n"
    b"2026-10-26 09:17:45 WARN keepalive timeout\n"
    b"2026-10-26 09:17:46 INFO reconnecting\n"
)


def password_from_env(username: str) -> str:
    name = f"SEED_{username.upper()}_PASSWORD"
    password = os.environ.get(name, "")
    if not password:
        raise SystemExit(f"Set {name} (see .env.example)")
    return password


def ensure_bucket() -> None:
    """Create the bucket in the local S3 stand-in only; in AWS it comes from Terraform."""
    settings = get_settings()
    if settings.s3_endpoint_url is None:
        return
    client = storage.get_s3_client()
    try:
        client.head_bucket(Bucket=settings.s3_bucket)
    except ClientError:
        region = client.meta.region_name
        options = (
            {}
            if region == "us-east-1"
            else {"CreateBucketConfiguration": {"LocationConstraint": region}}
        )
        client.create_bucket(Bucket=settings.s3_bucket, **options)


def ensure_user(db: Session, username: str, full_name: str, role: Role) -> User:
    user = db.scalar(select(User).where(User.username == username))
    if user is None:
        user = User(username=username, email=f"{username}@example.com", full_name=full_name)
        db.add(user)
    user.role = role
    user.password_hash = hash_password(password_from_env(username))
    return user


def ensure_tickets(db: Session, owner: User) -> dict[str, Ticket]:
    existing = {ticket.title: ticket for ticket in owner.tickets}
    for title, description, priority in TICKETS.get(owner.username, []):
        if title not in existing:
            existing[title] = Ticket(
                title=title, description=description, priority=priority, owner=owner
            )
            db.add(existing[title])
    return existing


def ensure_attachment(db: Session, ticket: Ticket, uploader: User) -> None:
    key = storage.object_key(ticket.id, ATTACHMENT_FILENAME)
    storage.upload(key, ATTACHMENT_CONTENT, "text/plain")
    if not any(a.filename == ATTACHMENT_FILENAME for a in ticket.attachments):
        ticket.attachments.append(
            Attachment(
                filename=ATTACHMENT_FILENAME,
                s3_key=key,
                content_type="text/plain",
                size=len(ATTACHMENT_CONTENT),
                uploaded_by=uploader.id,
            )
        )


def seed() -> None:
    ensure_bucket()
    with get_sessionmaker()() as db:
        users = {
            username: ensure_user(db, username, name, role) for username, name, role in ACCOUNTS
        }
        db.flush()
        tickets = {username: ensure_tickets(db, users[username]) for username in TICKETS}
        db.flush()
        vpn_ticket = tickets["alice"][TICKETS["alice"][0][0]]
        ensure_attachment(db, vpn_ticket, users["alice"])
        db.commit()
        logger.info(
            "Seeded %d accounts and %d tickets", len(users), sum(len(t) for t in tickets.values())
        )


def main() -> None:
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    seed()


if __name__ == "__main__":
    main()
