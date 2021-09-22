# -*- coding: utf-8 -*-
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from fastapi import HTTPException, status

from api.core.log.caishen_logger import logger

from .authentication import AuthenticationProviderMissmatch
from .authorization import UnAuthorizedUser
from .base import CaishenBaseException
from .database import DatabaseConnectionError


@asynccontextmanager
async def exception_handling() -> Optional[AsyncGenerator]:
    try:
        yield
    except DatabaseConnectionError as exc:
        logger.exception("Failed to connect to the database", repr(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error has occurred. Please try again.",
        )
    except UnAuthorizedUser as exc:
        log = exc.log
        logger.warning("Failed to authorize user", **log.dict())
        raise HTTPException(status_code=log.status_code, detail=log.msg)

    except AuthenticationProviderMissmatch as exc:
        auth_log = exc.log
        logger.exception(
            "Failed to authenticate user with AuthProvider", **auth_log.dict()
        )
        raise HTTPException(
            status_code=auth_log.status_code,
            detail=auth_log.msg,
        )
    except CaishenBaseException as exc:
        logger.exception(repr(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error has occurred. Please try again.",
        )
