# -*- coding: utf-8 -*-
from typing import Optional

from pydantic import BaseModel, Field
from pydantic.types import UUID4


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
