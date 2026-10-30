"""Registration and login (docs/app-spec.md, section 4.1)."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ticketing.db import get_db
from ticketing.models import User
from ticketing.schemas import Token, UserCreate, UserRead
from ticketing.security import create_access_token, hash_password, verify_password

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth"])

ALREADY_REGISTERED = "Username or email already registered"


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Annotated[Session, Depends(get_db)]) -> User:
    taken = db.scalar(
        select(User.id).where(or_(User.username == data.username, User.email == data.email))
    )
    if taken is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=ALREADY_REGISTERED)
    user = User(
        username=data.username,
        email=data.email,
        full_name=data.full_name,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        # A concurrent registration took the name between the check and the insert.
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=ALREADY_REGISTERED
        ) from None
    return user


@router.post("/login", response_model=Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> Token:
    user = db.scalar(select(User).where(User.username == form_data.username))
    if user is None or not verify_password(user.password_hash, form_data.password):
        # Logged here, not in a helper: the GT-06 rule analyses one function
        # (semgrep-rules/README.md).
        username = form_data.username.replace("\r", "\\r").replace("\n", "\\n")
        logger.warning("Failed login for user %s", username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=create_access_token(user))
