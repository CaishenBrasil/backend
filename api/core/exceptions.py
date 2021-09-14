# -*- coding: utf-8 -*-
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class CacheException(Exception):
    pass


class CacheConnectionError(CacheException):
    pass


class DatabaseException(Exception):
    pass


class UnknownDatabaseType(DatabaseException):
    pass


class DatabaseConnectionError(DatabaseException):
    pass


class AuthenticationException(Exception):
    pass


class UnknownAuthenticationProvider(AuthenticationException):
    pass


class AuthenticationProviderMismatch(AuthenticationException):
    def __init__(self, current_provider: str, msg: str) -> None:
        self.current_provider = current_provider


class AuthorizationException(Exception):
    pass


class UnauthorizedUser(AuthorizationException):
    pass


class DiscoveryDocumentError(AuthorizationException):
    pass


class ProviderConnectionError(AuthorizationException):
    pass


@asynccontextmanager
async def exception_handling() -> Optional[AsyncGenerator]:
    try:
        yield
    except DatabaseConnectionError as exc:
        logger.exception(f"Failed to connect to the database: {repr(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cannot serve results at the moment. Please try again.",
        )
    except UnauthorizedUser as exc:
        logger.warning(f"Failed to authorize user: {repr(exc)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authorized"
        )

    except AuthenticationProviderMismatch as exc:
        logger.exception(
            f"Failed to authenticate user because it's already registered \
            by another Authentication Provider: {exc.current_provider}"
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User is already registered using {exc.current_provider} authentication provider",
        )
    except Exception as exc:
        logger.exception(repr(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error has occurred. Please try again.",
        )
