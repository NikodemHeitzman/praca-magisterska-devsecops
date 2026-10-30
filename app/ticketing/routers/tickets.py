"""Tickets (docs/app-spec.md, sections 4.2 and 5)."""

import shutil
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import Select, select, text
from sqlalchemy.orm import Session

from ticketing import storage
from ticketing.config import get_settings
from ticketing.db import get_db
from ticketing.models import Role, Ticket, TicketStatus, User
from ticketing.schemas import StatusUpdate, TicketCreate, TicketDetail, TicketRead, TicketUpdate
from ticketing.security import get_current_user

router = APIRouter(prefix="/api/tickets", tags=["tickets"])

TICKET_NOT_FOUND = "Ticket not found"

# Columns a client may sort by; the name from the request is only a key here (GT-04).
SORT_FIELDS = {
    "created_at": Ticket.created_at,
    "priority": Ticket.priority,
    "status": Ticket.status,
    "title": Ticket.title,
}

# Deliberate logic error kept in the clean version (docs/app-spec.md, section 5): CLOSED has
# no entry, so changing the status of a closed ticket raises KeyError and returns 500.
# The GT-14 audit relies on it. Do not add the missing key.
ALLOWED_TRANSITIONS = {
    TicketStatus.OPEN: {TicketStatus.IN_PROGRESS, TicketStatus.CLOSED},
    TicketStatus.IN_PROGRESS: {TicketStatus.OPEN, TicketStatus.RESOLVED},
    TicketStatus.RESOLVED: {TicketStatus.OPEN, TicketStatus.CLOSED},
}


def can_access(user: User, ticket: Ticket) -> bool:
    return ticket.owner_id == user.id or user.role == Role.ADMIN


def visible_tickets(user: User) -> Select[tuple[Ticket]]:
    query = select(Ticket)
    if user.role != Role.ADMIN:
        query = query.where(Ticket.owner_id == user.id)
    return query


def get_accessible_ticket(db: Session, user: User, ticket_id: int) -> Ticket:
    # 404, not 403: do not reveal that another user's ticket exists.
    ticket = db.get(Ticket, ticket_id)
    if ticket is None or not can_access(user, ticket):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=TICKET_NOT_FOUND)
    return ticket


@router.post("", response_model=TicketRead, status_code=status.HTTP_201_CREATED)
def create_ticket(
    data: TicketCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Ticket:
    ticket = Ticket(**data.model_dump(), owner_id=user.id)
    db.add(ticket)
    db.commit()
    return ticket


@router.get("", response_model=list[TicketRead])
def list_tickets(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    status_filter: Annotated[TicketStatus | None, Query(alias="status")] = None,
    sort: str = "created_at",
    order: Literal["asc", "desc"] = "desc",
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[Ticket]:
    if sort not in SORT_FIELDS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"sort must be one of: {', '.join(SORT_FIELDS)}",
        )
    column = SORT_FIELDS[sort]
    query = visible_tickets(user)
    if status_filter is not None:
        query = query.where(Ticket.status == status_filter)
    query = query.order_by(column.asc() if order == "asc" else column.desc(), Ticket.id)
    return list(db.scalars(query.limit(limit).offset(offset)))


# Declared before /{ticket_id}, which would otherwise match "search".
@router.get("/search", response_model=list[TicketRead])
def search_tickets(
    q: Annotated[str, Query(min_length=1, max_length=100)],
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[Ticket]:
    statement = text(
        "SELECT * FROM tickets"
        " WHERE (title ILIKE :pattern OR description ILIKE :pattern)"
        " AND (:is_admin OR owner_id = :user_id)"
        " ORDER BY id"
    )
    params = {"pattern": f"%{q}%", "is_admin": user.role == Role.ADMIN, "user_id": user.id}
    return list(db.scalars(select(Ticket).from_statement(statement), params))


@router.get("/{ticket_id}", response_model=TicketDetail)
def read_ticket(
    ticket_id: int,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Ticket:
    ticket = db.get(Ticket, ticket_id)
    if ticket is None or not can_access(user, ticket):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=TICKET_NOT_FOUND)
    return ticket


@router.patch("/{ticket_id}", response_model=TicketRead)
def update_ticket(
    ticket_id: int,
    update: TicketUpdate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Ticket:
    ticket = get_accessible_ticket(db, user, ticket_id)
    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(ticket, field, value)
    db.commit()
    return ticket


@router.post("/{ticket_id}/status", response_model=TicketRead)
def change_status(
    ticket_id: int,
    update: StatusUpdate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Ticket:
    ticket = get_accessible_ticket(db, user, ticket_id)
    if update.status not in ALLOWED_TRANSITIONS[ticket.status]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot change status from {ticket.status} to {update.status}",
        )
    ticket.status = update.status
    db.commit()
    return ticket


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(
    ticket_id: int,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    ticket = get_accessible_ticket(db, user, ticket_id)
    keys = [attachment.s3_key for attachment in ticket.attachments]
    db.delete(ticket)
    db.commit()
    # After the commit: a failed S3 call leaves orphaned objects, never records without files.
    storage.delete(keys)
    shutil.rmtree(get_settings().attachment_cache_dir / str(ticket_id), ignore_errors=True)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
