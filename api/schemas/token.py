# -*- coding: utf-8 -*-
from typing import Optional

from pydantic import Field
from pydantic.types import UUID4

from .base import BaseModel


class Token(BaseModel):
    code: str
    token_type: str

    class Config:
        validate_assignment = True


class AuthToken(Token):
    token_type: str = Field(default="bearer", allow_mutation=False)


class AccessToken(Token):
    token_type: str = Field(default="bearer", allow_mutation=False)
    access_token: str


class CSRFToken(Token):
    token_type: str = Field(default="state", allow_mutation=False)


class ExternalAuthToken(Token):
    token_type: str = Field(default="bearer", allow_mutation=False)


class TokenPayload(BaseModel):
    sub: Optional[UUID4] = None


class FacebookAccessToken(BaseModel):
    token_type: str
    access_token: str
    expires_in: str
