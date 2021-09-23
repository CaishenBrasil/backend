# -*- coding: utf-8 -*-
from pydantic.networks import AnyHttpUrl

from .base import BaseModel
from .token import CSRFToken


class RequestUriParams(BaseModel):
    state: CSRFToken
    uri: AnyHttpUrl
