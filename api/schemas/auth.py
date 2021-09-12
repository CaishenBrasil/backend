# -*- coding: utf-8 -*-
from pydantic import BaseModel
from pydantic.networks import AnyHttpUrl

from .token import CSRFToken


class RequestUriParams(BaseModel):
    state: CSRFToken
    uri: AnyHttpUrl
