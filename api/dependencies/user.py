# -*- coding: utf-8 -*-
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from api import crud, models, schemas

from .auth import get_token_data
from .database import get_session


def get_current_user(
    session: Session = Depends(get_session),
    token_data: schemas.TokenPayload = Depends(get_token_data),
) -> models.User:
    user = crud.user.get(session, id=token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not validate credentials, try to re-login.",
        )
    return user
