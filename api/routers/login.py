# -*- coding: utf-8 -*-
from datetime import timedelta
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from api import crud, schemas
from api.core import security
from api.dependencies import get_session
from api.settings import settings

prefix = settings.API_VERSION_STR + "/login"
router = APIRouter(prefix=prefix, tags=["Login"])


@router.post("/access-token", response_model=schemas.Token)
def login_access_token(
    session: Session = Depends(get_session),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.user.authenticate(
        session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    token = schemas.Token(
        access_token=security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        token_type="bearer",
    )
    return token


@router.get("/google-login", tags=["Social Login"], description="Google Oauth Login")
def google_login() -> Dict:
    return {"message": "This is supposed to be the Google login endpoint"}


@router.get(
    "/facebook-login", tags=["Social Login"], description="Facebook Oauth Login"
)
def facebook_login() -> Dict:
    return {"message": "This is supposed to be the Facebook login endpoint"}
