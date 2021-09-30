# -*- coding: utf-8 -*-
from pydantic import AnyHttpUrl

from .base import BaseModel
from .token import CSRFToken


class RequestUriParams(BaseModel):
    state: CSRFToken
    uri: AnyHttpUrl


class FacebookAccessTokenParams(BaseModel):
    redirect_uri: AnyHttpUrl
    code: str
    client_id: str
    client_secret: str
