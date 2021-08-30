# -*- coding: utf-8 -*-
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError

from api import schemas
from api.settings import settings

token_url = settings.API_VERSION_STR + "/login/access-token"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=token_url)


def get_token_data(token: str = Depends(oauth2_scheme)) -> schemas.TokenPayload:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
        return token_data
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
