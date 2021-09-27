# -*- coding: utf-8 -*-
from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import EmailStr, Field
from pydantic.types import UUID4

from .base import BaseModel, BaseModelORM


class AuthProvider(str, Enum):
    GOOGLE = "GOOGLE"
    FACEBOOK = "FACEBOOK"
    LOCAL = "LOCAL"


class UserBase(BaseModelORM):
    name: str
    birth_date: date
    email: EmailStr
    is_admin: bool


class UserCreate(UserBase):
    auth_provider: AuthProvider


class UserLocalCreate(UserBase):
    password: str
    auth_provider: AuthProvider = Field(default="LOCAL", allow_mutation=False)


class UserRead(UserBase):
    id: UUID4
    created_at: datetime
    auth_provider: AuthProvider


class UserUpdate(UserBase):
    id: UUID4
    name: Optional[str]
    birth_date: Optional[date]
    email: Optional[EmailStr]
    auth_provider: Optional[AuthProvider]
    password: Optional[str]
    is_admin: Optional[bool]


# Users from Auth Providers


class ExternalUser(BaseModel):
    sub: str
    email: EmailStr
    name: str
