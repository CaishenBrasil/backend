# -*- coding: utf-8 -*-
from fastapi import Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api import crud, models, schemas
from api.core.exceptions import UnAuthorizedUser

from .auth.schemes import AccessTokenValidator
from .database import get_session

get_token_data = AccessTokenValidator()


async def get_current_user(
    session: AsyncSession = Depends(get_session),
    token_data: schemas.TokenPayload = Depends(get_token_data),
) -> models.User:
    user = await crud.user.get(session, id=token_data.sub)
    if user is None:
        raise UnAuthorizedUser(
            log=schemas.UnAuthorizedUserLog(
                file_name=__name__,
                function_name="get_current_user",
                detail="Could not fetch user from database with token sub claim",
                status_code=status.HTTP_404_NOT_FOUND,
                msg="Could not validate credentials, try to re-login.",
            )
        )
    return user
