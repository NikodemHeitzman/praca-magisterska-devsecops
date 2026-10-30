"""Ticket attachments.

See docs/app-spec.md, section 4.3, and docs/adr/0006-przechowywanie-zalacznikow-s3.md.
"""

import re
from pathlib import PurePosixPath
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ticketing import storage
from ticketing.config import get_settings
from ticketing.db import get_db
from ticketing.models import Attachment, User
from ticketing.routers.tickets import get_accessible_ticket
from ticketing.schemas import AttachmentRead
from ticketing.security import get_current_user

router = APIRouter(prefix="/api/tickets", tags=["attachments"])

ATTACHMENT_NOT_FOUND = "Attachment not found"


def clean_filename(raw: str | None) -> str:
    """Base name only (no directories), unsafe characters replaced with underscores."""
    name = PurePosixPath((raw or "").replace("\\", "/")).name
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)[-255:]
    if name.strip(".") == "":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Invalid file name"
        )
    return name


@router.post(
    "/{ticket_id}/attachments", response_model=AttachmentRead, status_code=status.HTTP_201_CREATED
)
def upload_attachment(
    ticket_id: int,
    file: UploadFile,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Attachment:
    ticket = get_accessible_ticket(db, user, ticket_id)
    settings = get_settings()
    filename = clean_filename(file.filename)
    if file.content_type not in settings.allowed_content_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Allowed types: {', '.join(settings.allowed_content_types)}",
        )
    content = file.file.read(settings.max_upload_bytes + 1)
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"File larger than {settings.max_upload_bytes} bytes",
        )
    taken = db.scalar(
        select(Attachment.id).where(
            Attachment.ticket_id == ticket.id, Attachment.filename == filename
        )
    )
    if taken is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="File name already used")

    key = storage.object_key(ticket.id, filename)
    storage.upload(key, content, file.content_type)
    attachment = Attachment(
        ticket_id=ticket.id,
        filename=filename,
        s3_key=key,
        content_type=file.content_type,
        size=len(content),
        uploaded_by=user.id,
    )
    db.add(attachment)
    db.commit()
    return attachment


@router.get("/{ticket_id}/attachments", response_model=list[AttachmentRead])
def list_attachments(
    ticket_id: int,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[Attachment]:
    return get_accessible_ticket(db, user, ticket_id).attachments


# {filename:path}: the GT-05 patch must be exploitable over HTTP, and a plain {filename}
# never receives an encoded "../" (decision of the author, 2026-10-30).
@router.get("/{ticket_id}/attachments/{filename:path}")
def download_attachment(
    ticket_id: int,
    filename: str,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> FileResponse:
    ticket = get_accessible_ticket(db, user, ticket_id)
    cache_dir = (get_settings().attachment_cache_dir / str(ticket.id)).resolve()
    path = (cache_dir / filename).resolve()
    if not path.is_relative_to(cache_dir):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ATTACHMENT_NOT_FOUND)

    if not path.is_file():
        attachment = db.scalar(
            select(Attachment).where(
                Attachment.ticket_id == ticket.id, Attachment.filename == filename
            )
        )
        if attachment is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ATTACHMENT_NOT_FOUND)
        path.parent.mkdir(parents=True, exist_ok=True)
        storage.download(attachment.s3_key, path)
    return FileResponse(path, filename=path.name)
