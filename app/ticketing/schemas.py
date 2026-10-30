"""Request and response models of the API."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from ticketing.models import Role


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=64, pattern=r"^[A-Za-z0-9_.-]+$")
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    full_name: str | None
    role: Role
    created_at: datetime


class UserProfileUpdate(BaseModel):
    """Fields a user may change in their own profile (no role: GT-20 adds it)."""

    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = None

    @field_validator("email")
    @classmethod
    def email_not_null(cls, value: str | None) -> str:
        # Optional in the request, but the column is NOT NULL.
        if value is None:
            raise ValueError("email cannot be null")
        return value


class RoleUpdate(BaseModel):
    role: Role


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
