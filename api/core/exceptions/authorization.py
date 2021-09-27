# -*- coding: utf-8 -*-
from typing import Any

from api.schemas import UnAuthorizedUserLog

from .base import CaishenBaseException


class AuthorizationException(CaishenBaseException):
    pass


class UnAuthorizedUser(AuthorizationException):
    def __init__(
        self,
        *args: Any,
        log: UnAuthorizedUserLog,
    ) -> None:
        self.log = log
        super().__init__(*args)
