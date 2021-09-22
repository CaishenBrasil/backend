# -*- coding: utf-8 -*-
from typing import Any

from api.schemas import AuthenticationProviderLog

from .base import CaishenBaseException


class AuthenticationException(CaishenBaseException):
    pass


class AuthenticationProviderException(AuthenticationException):
    def __init__(
        self,
        *args: Any,
        log: AuthenticationProviderLog,
    ) -> None:
        self.log = log
        super().__init__(*args)


class UnknownAuthenticationProvider(AuthenticationProviderException):
    pass


class AuthenticationProviderMissmatch(AuthenticationProviderException):
    pass


class DiscoveryDocumentError(AuthenticationProviderException):
    pass


class ProviderConnectionError(AuthenticationProviderException):
    pass
