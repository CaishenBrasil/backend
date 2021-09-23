# -*- coding: utf-8 -*-
from fastapi import Request, status
from fastapi.responses import JSONResponse

from api.core.log.caishen_logger import logger

from .authentication import AuthenticationProviderException
from .authorization import UnAuthorizedUser
from .database import DatabaseConnectionError


async def database_connection_error_handler(
    request: Request,
    exc: DatabaseConnectionError,
) -> JSONResponse:
    logger.exception("Failed to connect to the database", repr(exc))
    headers = getattr(exc, "headers", None)
    if headers:
        return JSONResponse(
            {"detail": "An error has occurred. Please try again."},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers=headers,
        )
    else:
        return JSONResponse(
            {"detail": "An error has occurred. Please try again."},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


async def unauthorized_user_handler(
    request: Request, exc: UnAuthorizedUser
) -> JSONResponse:
    logger.warning(**exc.log.dict())
    headers = getattr(exc, "headers", None)
    if headers:
        return JSONResponse(
            {"detail": exc.log.msg},
            status_code=exc.log.status_code,
            headers=headers,
        )
    else:
        return JSONResponse(
            {"detail": exc.log.msg},
            status_code=exc.log.status_code,
        )


async def authentication_provider_error_handler(
    request: Request,
    exc: AuthenticationProviderException,
) -> JSONResponse:
    logger.error(**exc.log.dict())
    headers = getattr(exc, "headers", None)
    if headers:
        return JSONResponse(
            {"detail": exc.log.msg},
            status_code=exc.log.status_code,
            headers=headers,
        )
    else:
        return JSONResponse(
            {"detail": exc.log.msg},
            status_code=exc.log.status_code,
        )
